import os

import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
#============= 系统自定义模块 =============
from image_ocr.card_processor import OptimizedCardProcessor
from image_ocr.process_utils import merge_results
#=========================================

def init_process():
    """初始化子进程"""
    global processor
    processor = OptimizedCardProcessor()


def process_batch_wrapper(args):
    """批量处理包装器"""
    chunk, folder_path, patterns = args
    return processor.process_batch(chunk, folder_path, patterns)


def calculate_processes(file_count, max_processes=None):
    """动态计算最优进程数"""
    cpu_count = os.cpu_count() or 4
    max_p = min(cpu_count * 2, max_processes) if max_processes else cpu_count * 2
    return min(max_p, max(4, (file_count // 10) + 1))

def optimized_parallel_process(folder_path, num_processes=None):
    """并行处理流程
    参数：
        folder_path: 待处理图片目录路径
        num_processes: 最大允许进程数 (None表示自动计算)
    流程：
        1. 配置正则表达式模式
        2. 动态计算进程数
        3. 分块处理图像文件
        4. 并行执行OCR识别
        5. 合并处理结果
    """
    # 配置证件号码正则表达式
    patterns = {
        "idcard": r"(\d{17}[\dXx]|\d{15}[\dXx])",  # 身份证规则：15位或17位数字（末位允许X）
        "bankcard": r"\d{16,20}",                   # 银行卡规则：16-20位连续数字
    }

    # 文件列表预处理
    file_list = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpeg')]
    total_files = len(file_list)
    num_processes = calculate_processes(total_files, num_processes)  # 动态计算进程数
    chunk_size = max(10, (total_files // num_processes) + 1)         # 最小分块10文件
    print(f"将文件分块： {chunk_size}/块 ")
    print(f"使用 {num_processes} 个处理器并行分析分片...\n")
    file_chunks = [file_list[i:i + chunk_size] for i in range(0, total_files, chunk_size)]

    # 多进程执行
    with ProcessPoolExecutor(max_workers=num_processes, initializer=init_process) as executor:
        tasks = [(chunk, folder_path, patterns) for chunk in file_chunks]
        results = list(tqdm(
            executor.map(process_batch_wrapper, tasks),
            total=len(file_chunks),
            desc="Processing Images"  # 进度条提示
        ))
    print("图片处理成功")
    # 合并结果
    final_result = []
    for batch in results:
        final_result.extend(batch)
    return pd.DataFrame(final_result)