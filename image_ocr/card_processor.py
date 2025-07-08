import gc
import os
import re
import cv2
import numpy as np
from paddleocr import PaddleOCR
from collections import defaultdict
from config.PATH import OCR_model


class OptimizedCardProcessor:
    """证件处理器"""

    def __init__(self):
        self.id_ocr = None
        self.bank_ocr = None

    def _load_id_model(self):
        """加载身份证专用模型"""
        self.id_ocr = PaddleOCR(
            use_angle_cls=False,  # 关闭方向分类（身份证无需角度检测）
            cls_model_dir=os.path.join(OCR_model, 'ch_ppocr_mobile_v2.0_cls_infer'),  # 移动端分类模型
            det_model_dir=os.path.join(OCR_model, 'ch_PP-OCRv3_det_infer'),  # 轻量版检测模型
            rec_model_dir=os.path.join(OCR_model, 'ch_PP-OCRv3_rec_infer'),  # 轻量版识别模型
            det_db_thresh=0.3,  # 文本检测阈值（低值提升召回率）
            det_db_box_thresh=0.5,  # 文本框置信度阈值
            enable_mkldnn=True,  # 启用Intel数学加速库
            use_tensorrt=False,  # 禁用NVIDIA加速（默认配置）
            show_log=False  # 关闭调试日志
        )
        # 模型预热
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.id_ocr.ocr(dummy_img, cls=False)
        return self.id_ocr

    def _load_bank_model(self):
        """加载银行卡专用模型"""
        self.bank_ocr = PaddleOCR(
            use_angle_cls=True,  # 启用方向分类（银行卡可能存在旋转）
            cls_model_dir=os.path.join(OCR_model, 'ch_ppocr_mobile_v2.0_cls_infer'),  # 移动端分类模型
            det_model_dir=os.path.join(OCR_model, 'ch_ppocr_server_v2.0_det_infer'),  # 服务端检测模型
            rec_model_dir=os.path.join(OCR_model, 'ch_ppocr_server_v2.0_rec_infer'),  # 服务端识别模型
            det_db_unclip_ratio=2.0,  # 文本框扩展比例（适应长文本）
            enable_mkldnn=True,  # 启用Intel加速
            use_tensorrt=False,  # 保持与身份证模型一致
            show_log=False  # 统一日志配置
        )
        # 模型预热
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.bank_ocr.ocr(dummy_img, cls=True)
        return self.bank_ocr

    def _release_model(self, model_type):
        """
        显式释放OCR模型内存
        
        参数:
            model_type (str): 模型类型标识
                - 'id'  释放身份证识别模型
                - 'bank' 释放银行卡识别模型
        
        功能:
            1. 删除模型实例引用
            2. 触发Python垃圾回收机制
            3. 防止大模型内存泄漏
        
        注意事项:
            - 释放后需重新初始化才能使用对应模型
            - 需显式调用gc.collect()确保立即回收
            - 参数校验已在调用前完成
        """
        if model_type == 'id' and self.id_ocr:
            del self.id_ocr
            self.id_ocr = None
        elif model_type == 'bank' and self.bank_ocr:
            del self.bank_ocr
            self.bank_ocr = None
        gc.collect()

    @staticmethod
    def extract_number(text, pattern):
        """号码提取"""
        clean_text = re.sub(r'\s+', '', text)
        match = re.search(pattern, clean_text)

        #金卡处理逻辑
        if match is None:
            return "6222" + re.search(r"\d{12}", clean_text).group()
        else:
            matched_str = match.group()
            if matched_str.endswith('6222'):
                # 取最后16位数字
                last_16 = matched_str[-16:]
                # 确保最后4位是6222（可能因截取位置变化）
                if last_16.endswith('6222'):
                    return '6222' + last_16[:12]
            elif matched_str.startswith('6222'):
                return matched_str[:16]
            return matched_str


    def _process_single(self, filename, folder_path, patterns, result_dict):
        """
        处理单个证件图片文件，执行OCR识别和信息提取
        
        参数:
            filename (str): 带分类的图片文件名（格式：手机号_类型_时间戳.jpg）
            folder_path (str): 图片文件所在目录路径
            patterns (dict): 正则表达式模式字典
                - idcard: 身份证号码匹配模式
                - bankcard: 银行卡号匹配模式
            result_dict (dict): 结果收集字典（按手机号聚合）
        
        处理流程:
            1. 解析文件名获取手机号标识
            2. 初始化结果条目（防止空值）
            3. 根据文件名分类处理:
               - 身份证: 加载专用模型，提取身份证号
               - 银行卡: 加载专用模型，提取银行卡号
            4. 及时释放图片内存（防止大文件累积）
        
        注意事项:
            - 使用cv2.imdecode支持中文路径读取
            - OCR结果进行正则二次校验
            - 异常处理覆盖文件损坏/格式错误等场景
        """
        try:
            parts = filename.split('_')
            phone = parts[0]

            # 初始化结果条目
            if phone not in result_dict:
                result_dict[phone] = {"phone": phone, "idcard": "", "bankcard": ""}
            img_path = os.path.join(folder_path, filename)

            # 动态选择处理流程
            if "idcard" in filename:
                img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                ocr_result = self.id_ocr.ocr(img, cls=False)
                ocr_text = " ".join([line[1][0] for line in ocr_result[0]])
                result_dict[phone]["idcard"] = self.extract_number(ocr_text, patterns['idcard'])
                del img

            elif "bankcard" in filename:
                img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                ocr_result = self.bank_ocr.ocr(img, cls=False)
                ocr_text = " ".join([line[1][0] for line in ocr_result[0]])
                result_dict[phone]["bankcard"] = self.extract_number(ocr_text, patterns['bankcard'])
                del img

        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")

    def process_batch(self, file_list, folder_path, patterns):
        """
        批量处理证件图片文件
        
        参数:
            file_list (list): 待处理文件路径列表
            folder_path (str): 图片存储根目录
            patterns (dict): 正则匹配模式字典
                - idcard: 身份证正则
                - bankcard: 银行卡正则
        
        处理流程:
            1. 按证件类型分组文件（身份证/银行卡分离处理）
            2. 动态加载专用OCR模型（按需初始化）
            3. 顺序处理同类文件（保证内存可控）
            4. 处理完成后立即释放模型资源
        
        返回:
            list[dict]: 结构化结果列表，格式:
                [{
                    "phone": "用户手机号",
                    "idcard": "身份证号码",
                    "bankcard": "银行卡号"
                }]
        
        注意事项:
            - 采用惰性加载策略优化内存使用
            - 同类文件批量处理减少模型切换开销
            - 显式释放图片和模型内存防止泄漏
            - 异常文件自动跳过并记录日志
        """
        result_dict = defaultdict(dict)

        # 按文件类型分组处理
        id_files = [f for f in file_list if 'idcard' in f]
        bank_files = [f for f in file_list if 'bankcard' in f]

        # 处理身份证件
        if id_files:
            if not self.id_ocr:
                self._load_id_model()
            for filename in id_files:
                self._process_single(filename, folder_path, patterns, result_dict)
            self._release_model('id')

        # 处理银行卡件
        if bank_files:
            if not self.bank_ocr:
                self._load_bank_model()
            for filename in bank_files:
                self._process_single(filename, folder_path, patterns, result_dict)
            self._release_model('bank')

        return list(result_dict.values())