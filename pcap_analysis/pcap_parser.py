from collections import defaultdict
import json
import subprocess
import os
#============= 系统自定义模块 =============
from pcap_analysis.flow_processor import process_flow
#=========================================

def extract_http_requests(pcap_file, tshark_path):
    """
    功能: 使用tshark解析PCAP文件, 提取HTTP请求数据
    输入: 
        pcap_file: PCAP文件路径 (str)
        tshark_path: TShark工具路径 (str)
    输出: 
        defaultdict: 按网络流分组的请求字典，结构为：
            {(src_port, stream_id): [请求字典1, 请求字典2...]}
            请求字典结构: {'uri': str, 'body': str}
    调用关系: 被report_generator调用

    实现步骤：
    1. 构建tshark命令行参数
    2. 执行命令并捕获JSON输出
    3. 解析JSON数据提取关键字段
    4. 按网络流分组请求数据
    """
    http_requests = defaultdict(list)

    # 构建tshark命令行（过滤HTTP请求，输出JSON格式）
    cmd = [
        tshark_path,
        '-r', pcap_file,        # 输入文件
        '-Y', 'http.request',  # 过滤HTTP请求
        '-T', 'json',          # 输出JSON格式
        '-e', 'tcp.srcport',   # 提取源端口
        '-e', 'tcp.stream',    # 提取流ID
        '-e', 'http.request.uri',  # 提取请求URI
        '-e', 'http.file_data'     # 提取请求体
    ]

    try:
        # 执行命令（超时由外部控制，编码使用UTF-8，替换错误字符）
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        
        # 检查命令执行状态
        if result.returncode != 0:
            return None

        # 解析JSON输出（处理空输出情况）
        packets = json.loads(result.stdout) if result.stdout else []

        # 遍历所有数据包
        for pkt in packets:
            try:
                layers = pkt['_source']['layers']
                
                # 提取关键字段（处理字段不存在的情况）
                src_port = layers.get('tcp.srcport', [''])[0]    # 源端口
                stream_id = layers.get('tcp.stream', [''])[0]    # 流ID
                uri = layers.get('http.request.uri', [''])[0]    # 请求URI
                body = layers.get('http.file_data', [''])[0]     # 请求体
                
                # 构建流标识键（源端口 + 流ID）
                flow_key = (src_port, stream_id)
                
                # 存储请求数据（无请求体时填充占位符）
                http_requests[flow_key].append({
                    'uri': uri,
                    'body': body if body else '无请求体'
                })
            except KeyError:  # 跳过字段缺失的数据包
                continue

        return http_requests

    except Exception as e:  # 捕获所有解析异常
        print(f"[解析异常] 文件: {os.path.basename(pcap_file)} | 错误: {str(e)}")
        return None

def process_chunk(args):
    """
    处理单个分片文件的完整流程
    输入:
        args: 元组 (分片路径, tshark路径, 图片输出目录)
            chunk_path: PCAP分片文件路径
            tshark_path: TShark工具路径
            image_output_dir: 图片输出目录
    输出:
        list: 处理结果列表，元素为 (流标识, 敏感信息字典)
    
    处理流程:
    1. 调用extract_http_requests解析分片中的HTTP请求
    2. 遍历所有网络流进行敏感数据处理
    3. 清理临时分片文件（如果分片在临时目录中）
    4. 返回当前分片的所有处理结果
    
    注意:
    - 使用串行处理替代内部进程池，避免多级并行带来的复杂性
    - 临时分片文件会在处理后立即删除，防止磁盘空间占用
    """
    # 解包参数
    chunk_path, tshark_path, image_output_dir = args
    
    # 提取当前分片的HTTP请求数据
    http_requests = extract_http_requests(chunk_path, tshark_path)
    results = []

    if http_requests:
        # 生成流处理参数列表（flow_key, 请求列表, 输出目录）
        flow_args_list = [(flow_key, reqs, image_output_dir) 
                         for flow_key, reqs in http_requests.items()]
        
        # 串行处理每个网络流（保持与上层并行逻辑的解耦）
        for flow_args in flow_args_list:
            results.append(process_flow(flow_args))

    # 清理临时文件（仅处理分片生成的文件）
    if "temp_pcap_chunks" in chunk_path:
        try:
            os.remove(chunk_path)  # 立即删除不再需要的分片
        except Exception:  # 忽略所有删除异常（文件可能已被删除）
            pass

    return results