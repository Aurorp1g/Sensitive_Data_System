import pandas as pd
import os
#============= 系统自定义模块 =============
from config.PATH import Temp_result_1, Temp_result_2, Final_result
#=========================================

if __name__ == "__main__":
    print(f'\n\033[1;32m▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣')
    print(f'    📊 数据整合阶段     ')
    print(f'▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣\033[0m')
    print('\n')
    try:
        print(f'\n\033[1;32m============ 合并分析结果开始 ===========\033[0m')
        # 读取两个 Excel 文件
        df1 = pd.read_csv(Temp_result_1, dtype={'username': str, 'password': str,'name': str, 'phone': str})
        df2 = pd.read_csv(Temp_result_2, dtype={'phone': str,'idcard': str ,'bankcard': str})

        # 根据 'phone' 列合并两个表格
        # 使用 'inner' 表示只保留两个表中都有的 'phone' 值
        # 使用 'outer' 表示保留所有 'phone' 值
        merged_df = pd.merge(df1, df2, on='phone', how='inner')

        # 保存合并后的结果到新的 Excel 文件
        # 在保存结果前创建目录（如果不存在）
        output_dir = os.path.dirname(Final_result)
        if output_dir:  
            # 当路径包含目录时才创建
            os.makedirs(output_dir, exist_ok=True)

        merged_df.to_csv(Final_result, index=False)
        print(f"合并完成，结果已保存到 {Final_result}")
        print(f"\n\033[1;32m============ 合并分析结果结束 ===========\033[0m")
    except Exception as e:
        print(f"合并过程中发生错误: {str(e)}")
        exit(1)