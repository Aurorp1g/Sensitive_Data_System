import tkinter as tk
from tkinter import filedialog
import time
#============= 系统自定义模块 =============
from config.PATH import TSHARK_PATH, Temp_img, Temp_result_1
#=========================================

'''系统核心模块调用'''
from pcap_analysis.report_generator import *

# 日志初始化
from utils.logger import system_logger

if __name__ == "__main__":
    system_logger.info("=== 程序启动 ===")
    try:
        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()
        
        # 弹出文件选择对话框
        input_pcap = filedialog.askopenfilename(
            title="选择PCAP文件",
            filetypes=[("PCAP文件", "*.pcap"), ("所有文件", "*.*")]
        )
        
        # 未选择文件
        if not input_pcap:
            print("未选择文件，程序退出")
            exit(1)       
        
        print('\n\033[1;36m╔══════════════════════════════════╗')
        print(f'║       🚀 预处理分析PCAP文件      ║')
        print('╚══════════════════════════════════╝\033[0m')

        start_time = time.time()
        try:
            # 路径设置
            csv_output_file, image_output_dir=Temp_result_1, Temp_img
            # 处理大文件
            process_large_pcap(input_pcap, TSHARK_PATH, csv_output_file, image_output_dir)
        except Exception as e:
            error_msg = f"分析失败 | 错误类型: {type(e).__name__} | 原因: {str(e)}"
            print(f"❌ {error_msg}")
            # 合并后的日志记录，包含完整堆栈信息
            system_logger.error(f"{error_msg}\n程序异常终止", exc_info=True)
        finally:
            print(f"\n总耗时: {time.time() - start_time:.2f}秒")
            print(f"\n\033[1;36m============ 预处理分析pcap 结束 ===========\033[0m")
            
            # 内存释放代码
            root.destroy()  # 彻底销毁Tk对象
            if 'input_pcap' in locals():
                del input_pcap  # 释放大文件引用
            import gc
            gc.collect()  # 强制垃圾回收

        exit(0)  # 确保程序正常退出
    except Exception as outer_e:  # 外层异常处理
        system_logger.critical(f"系统级错误: {str(outer_e)}", exc_info=True)
        print(f"⚠ 发生系统级错误，详情请查看日志文件")
        print(f"程序异常终止")
        exit(1)
    