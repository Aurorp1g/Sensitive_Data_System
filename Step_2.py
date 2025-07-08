import time
#============= 系统自定义模块 =============
from config.PATH import  Temp_img, Temp_result_2
from image_ocr.parallel import optimized_parallel_process
#=========================================

if __name__ == "__main__":
    print(f'\n\033[1;35m╭{"─"*10} 光学字符识别(OCR)引擎 {"─"*10}╮')
    print(f'│            🎯 正在处理图片数据            │')
    print(f'╰{"─"*43}╯\033[0m')
    try:
        start_time = time.time()

        # 配置参数
        input_folder = Temp_img
        output_path = Temp_result_2

        # 执行处理
        result_df = optimized_parallel_process(input_folder, num_processes=8)

        # 保存结果
        result_df.to_csv(output_path, index=False)

        # 输出统计信息
        elapsed_time = time.time() - start_time
        print(f"\n处理完成！共处理 {len(result_df)} 条记录")
        print(f"总耗时: {elapsed_time:.2f} 秒")
        print(f"平均速度: {len(result_df) / max(elapsed_time, 0.1):.1f} 条/秒")
        print(f"结果已保存至: {output_path}")
        print(f"\n\033[1;35m============ 图像OCR分析结束 ===========\033[0m")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        exit(1)