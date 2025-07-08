import os
# ============= 系统自定义模块 =============
from pcap_analysis.data_processor import *
import cv2
import numpy as np
# =========================================


def crop_by_ratio(img, x1_ratio, y1_ratio, x2_ratio, y2_ratio, quality, color):
    """
    按比例裁剪图像并压缩
    参数：
        img: 输入图像 (numpy数组，BGR格式)
        x1_ratio: 水平起始位置比例 (0.0~1.0，相对于图像宽度)
        y1_ratio: 垂直起始位置比例 (0.0~1.0，相对于图像高度)
        x2_ratio: 水平结束位置比例 (0.0~1.0，必须大于x1_ratio)
        y2_ratio: 垂直结束位置比例 (0.0~1.0，必须大于y1_ratio)
        quality: JPEG压缩质量 (0-100，100为最高质量)
        color: 是否保留色彩 (True=彩色模式，False=转为灰度)
    返回：
        成功: JPEG编码的字节数据 (numpy数组)
        失败: None
    注意:
        1. 自动处理坐标越界（超出图像尺寸自动截断）
        2. 支持异常图像输入（返回None保证流程继续）
    """
    # 获取原始图像尺寸
    height, width = img.shape[:2]
    
    # 计算实际像素坐标（确保坐标不越界）
    x1 = max(0, int(width * x1_ratio))
    y1 = max(0, int(height * y1_ratio))
    x2 = min(width, int(width * x2_ratio))
    y2 = min(height, int(height * y2_ratio))

    ext = '.jpeg'
    try:
        if color:
            # 彩色模式直接裁剪
            _, encoded = cv2.imencode(ext, img[y1:y2, x1:x2], 
                                    [cv2.IMWRITE_JPEG_QUALITY, quality])
        else:
            # 灰度模式：转换颜色空间后裁剪
            gray_img = cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            _, encoded = cv2.imencode(ext, gray_img,
                                    [cv2.IMWRITE_JPEG_QUALITY, quality])
        return encoded
    except Exception as e:
        # 记录裁剪失败情况（调用方处理日志）
        return None




def process_flow(args):
    """
    功能: 处理单个网络流中的所有请求
    输入: 
        args: 元组 (流标识, 请求列表, 图片输出目录)
            flow_key: 流标识元组 (源端口, 流ID)
            requests: 当前流的所有HTTP请求列表
            image_output_dir: 图片输出目录路径
    输出: 
        元组 (流标识, 敏感信息字典)，字典包含以下可能字段：
            {'username', 'password', 'phone', 'name'}
    调用关系: 被report_generator调用

    处理逻辑：
    1. 初始化敏感信息字典
    2. 遍历流中的每个HTTP请求：
       - 登录请求：解析用户名密码
       - 调查表请求：解析电话号码和银行卡图片
       - 验证请求：解析身份证图片
    3. 合并多次请求中的敏感信息（后出现的值覆盖前值）
    4. 返回最终提取的敏感信息

    图片命名规则：
    银行卡图片: <phone>_bankcard.jpeg（若phone不存在则使用flow_<流ID>）
    身份证图片: 原始文件名_idcard.jpeg（保留原始文件名前缀）
    """
    # 解包参数（流标识，请求列表，图片目录）
    flow_key, requests, image_output_dir = args
    
    # 初始化敏感信息存储（使用字典维护最新值）
    sensitive_info = {
        'username': None, 
        'password': None, 
        'phone': None, 
        'name': None
    }

    # 遍历当前流的所有HTTP请求
    for req in requests:
        url = req.get('uri', '')
        body = req.get('body', '')
        if body == '无请求体':  # 跳过无请求体的请求
            continue

        # 处理登录请求（/login.php）
        if url.startswith("/login.php"):
            # 解析URL编码参数并更新敏感信息
            params = parse_sensitive_data(body)
            sensitive_info.update({
                k: v for k, v in params.items() 
                if k in sensitive_info
            })

        # 处理调查表请求（/survey.php）
        elif url.startswith("/survey.php"):
            # 解析multipart数据（包含表单字段和银行卡图片）
            fields, images = parse_multipart_data(body)
            sensitive_info.update({
                k: v for k, v in fields.items() 
                if k in sensitive_info
            })

            # 处理银行卡图片（固定裁剪参数）
            for filename, img_data in images:
                try:
                    # 解码图片并裁剪有效区域（保留卡号区域）
                    img = cv2.imdecode(
                        np.frombuffer(img_data, dtype=np.uint8), 
                        cv2.IMREAD_COLOR
                    )
                    processed = crop_by_ratio(
                        img, 
                        x1_ratio=0.05,   # 左侧留空5% 
                        y1_ratio=0.4,    # 顶部留空40%
                        x2_ratio=0.95,   # 右侧留空5%
                        y2_ratio=0.75,   # 底部留空25%
                        quality=100,     # 最高质量保存
                        color=True       # 保留彩色
                    )
                    
                    if processed is not None:
                        # 生成文件名：优先使用phone字段，否则用流ID
                        phone_tag = sensitive_info.get('phone') or f"flow_{flow_key[1]}"
                        filename = f"{phone_tag}_bankcard.jpeg"
                        # 保存裁剪后的银行卡图片
                        with open(os.path.join(image_output_dir, filename), 'wb') as f:
                            f.write(processed.tobytes())
                except Exception as e:
                    print(f"银行卡图像处理失败: {str(e)}")

        # 处理验证请求（/verify.php）
        elif url.startswith("/verify.php"):
            # 解析multipart数据（仅包含身份证图片）
            _, images = parse_multipart_data(body)
            
            for filename, img_data in images:
                try:
                    # 解码图片并裁剪有效区域（保留身份证底部信息）
                    img = cv2.imdecode(
                        np.frombuffer(img_data, dtype=np.uint8), 
                        cv2.IMREAD_COLOR
                    )
                    processed = crop_by_ratio(
                        img, 
                        x1_ratio=0.29,   # 左侧留空29%
                        y1_ratio=0.78,   # 顶部留空78%
                        x2_ratio=0.8,    # 右侧留空20%
                        y2_ratio=0.9,    # 底部留空10%
                        quality=40,      # 较低质量保存
                        color=False      # 转为灰度
                    )
                    
                    if processed is not None:
                        # 生成文件名：保留原始文件名前缀
                        phone_tag = os.path.splitext(filename)[0]
                        filename = f"{phone_tag}_idcard.jpeg"
                        # 保存处理后的身份证图片
                        with open(os.path.join(image_output_dir, filename), 'wb') as f:
                            f.write(processed.tobytes())
                except Exception as e:
                    print(f"身份证图像处理失败: {str(e)}")

    return (flow_key, sensitive_info)
