import urllib.parse


def parse_multipart_data(body_hex):
    """
    功能: 解析multipart/form-data格式的请求体, 提取普通表单字段和图片文件
    输入：十六进制字符串格式的请求体
    输出：元组(fields, images), 其中fields为普通字段字典, images为图片列表（文件名, 二进制内容）
    调用关系: 被flow_processor调用
    
    实现逻辑：
    1. 将十六进制字符串转换为原始字节数据
    2. 提取multipart边界标识
    3. 分割并处理每个数据块
    4. 解析头部信息判断字段类型
    5. 分离普通字段和图片文件
    """
    fields = {}
    images = []
    
    # 尝试将十六进制转换为字节数据（处理无效十六进制输入）
    try:
        data = bytes.fromhex(body_hex)
    except ValueError:
        return fields, images  # 返回空结果

    # 提取multipart边界（首行以--开头）
    try:
        boundary_line = data.split(b'\r\n', 1)[0].strip(b'-')
    except IndexError:  # 处理空数据的情况
        return fields, images

    # 遍历每个数据块（按边界分割）
    for part in data.split(boundary_line):
        part = part.strip(b'\r\n-')  # 清理分隔符残留
        if not part:  # 跳过空块
            continue

        # 分割头部和内容（\r\n\r\n分隔）
        try:
            headers_raw, content = part.split(b'\r\n\r\n', 1)
        except ValueError:  # 处理格式错误的分块
            continue

        # 解析头部信息（使用小写键名）
        headers = {}
        for line in headers_raw.split(b'\r\n'):
            try:
                line_decoded = line.decode('utf-8', errors='replace')
                if ':' in line_decoded:
                    key, value = line_decoded.split(":", 1)
                    headers[key.strip().lower()] = value.strip()
            except UnicodeDecodeError:  # 跳过无效编码行
                continue

        # 必须包含content-disposition头
        if 'content-disposition' not in headers:
            continue

        # 解析字段名和文件名（支持带引号的参数）
        cd = headers['content-disposition']
        field_name = filename = None
        for item in cd.split(";"):
            item = item.strip()
            if item.startswith("name="):
                field_name = item.split("=", 1)[1].strip('"')
            elif item.startswith("filename="):
                filename = item.split("=", 1)[1].strip('"')

        if not field_name:  # 无有效字段名则跳过
            continue

        # 分类处理字段和图片
        if filename:
            # 仅接受image/开头的MIME类型
            if 'content-type' in headers and headers['content-type'].startswith('image/'):
                images.append((filename, content))
        else:
            # 解码普通字段内容（忽略解码错误）
            try:
                fields[field_name] = content.decode('utf-8').strip()
            except UnicodeDecodeError:
                pass

    return fields, images

def parse_sensitive_data(body_hex):
    """
    功能: 解析URL编码的请求体
    输入：十六进制字符串格式的请求体
    输出：敏感参数字典
    调用关系: 被flow_processor调用
    """
    
    try:
        # 将十六进制字符串转换为字节数据（支持网络抓包数据格式）
        # 使用errors='replace'处理非法字符（如\x00）
        text = bytes.fromhex(body_hex).decode('utf-8', errors='replace')
    except Exception:  # 捕获所有可能的转换异常（如空输入、奇数字节长度）
        text = ''  # 初始化空字符串保证后续处理
    
    # 使用urllib解析URL编码参数（支持重复键取首值）
    # parse_qs返回格式示例：{'user': ['admin'], 'pass': ['123']}
    params = urllib.parse.parse_qs(text)
    
    # 将列表值转换为单值（根据业务需求取第一个有效值）
    return {k: v[0] for k, v in params.items()}