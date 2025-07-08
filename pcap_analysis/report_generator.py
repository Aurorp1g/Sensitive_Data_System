import os
import csv
import subprocess
import glob
from collections import defaultdict
from multiprocessing import cpu_count, get_context
from tqdm import tqdm
#============= 系统自定义模块 =============
from pcap_analysis.pcap_parser import process_chunk
import shutil
#=========================================

def process_large_pcap(pcap_file, tshark_path,
                       csv_output_file='sensitive_data.csv',
                       image_output_dir='extracted_images'):
    """
    功能: 处理大文件同时提取图片与敏感数据, 生成CSV报告
    调用链: 
        1. 调用pcap_parser进行PCAP解析
        2. 使用multiprocessing并行处理
        3. 调用flow_processor处理每个流
        4. 生成最终CSV报告
        5. 调用logger记录日志
    输入: 
        pcap_file: PCAP文件路径 (str)
        tshark_path: TShark工具路径 (str)
        csv_output_file: 输出CSV文件路径，默认'sensitive_data.csv' (str)
        image_output_dir: 图片输出目录，默认'extracted_images' (str)
    输出: 
        生成CSV文件 + 图片文件
        返回: None
    """
    # 初始化输出目录（自动创建不存在的目录）
    os.makedirs(image_output_dir, exist_ok=True)

    # 分片处理逻辑（当文件大小超过1GB时进行分片）
    temp_dir = None
    if os.path.getsize(pcap_file) > 1 * 1024 ** 3:  # 1GB阈值
        temp_dir = "temp_pcap_chunks"
        os.makedirs(temp_dir, exist_ok=True)

        # 使用editcap工具分割大文件（每50万包为一个分片）
        editcap_path = os.path.join(os.path.dirname(tshark_path), "editcap")
        subprocess.run([
            editcap_path,
            '-c', '500000',  # 每个分片包含的包数量
            pcap_file,
            os.path.join(temp_dir, "chunk")  # 分片文件前缀
        ], check=True)

        # 获取排序后的分片文件列表
        chunks = sorted(glob.glob(os.path.join(temp_dir, "chunk*")))
    else:
        chunks = [pcap_file]  # 小文件直接处理

    # 动态计算核心数（使用75%的CPU核心，至少保留2个核心）
    num_chunks = len(chunks)
    cpu_cores = cpu_count()
    pool_size = min(num_chunks, max(2, int(cpu_cores * 0.75)))
    print(f"分割为 {num_chunks} 个分片")
    print(f"使用 {pool_size} 个处理器并行分析分片...")

    # 多进程处理分片（使用spawn上下文避免继承锁问题）
    final_results = defaultdict(dict)
    with get_context('spawn').Pool(pool_size) as pool:
        # 准备任务参数（分片路径，tshark路径，图片输出目录）
        args = [(chunk, tshark_path, image_output_dir) for chunk in chunks]

        # 使用tqdm显示整体进度（每个分片处理完成后更新进度条）
        with tqdm(total=len(chunks), desc="处理分片") as pbar:
            for chunk_result in pool.imap(process_chunk, args):
                # 合并分片处理结果（保留最新出现的数据）
                for flow_key, sensitive_info in chunk_result:
                    current = final_results.get(flow_key, {})
                    # 按字段优先级更新数据（后出现的值覆盖先出现的）
                    for k in ['username', 'password', 'phone', 'name']:
                        if sensitive_info.get(k):
                            current[k] = sensitive_info[k]
                    final_results[flow_key] = current
                pbar.update(1)

    # 生成最终报告（CSV格式，UTF-8编码）
    with open(csv_output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password", "name", "phone"])  # CSV表头
        for info in final_results.values():
            writer.writerow([
                info.get('username', ''),
                info.get('password', ''),
                info.get('name', ''),
                info.get('phone', '')
            ])

    # 清理临时目录（仅当创建过分片目录时执行）
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    print(f"处理完成，结果已保存到: {csv_output_file}")