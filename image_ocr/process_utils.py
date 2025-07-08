import pandas as pd

def merge_results(all_results):
    """高效合并结果
    参数：
        all_results: 多批次处理结果列表
    功能：
        1. 按手机号聚合数据
        2. 保留每个手机号的首个有效身份证/银行卡信息
        3. 自动过滤重复记录
    返回：
        pandas.DataFrame 最终合并结果
    """
    print("开始合并")
    result_dict = {}  # 使用字典避免重复查询
    for batch in all_results:
        for item in batch:
            phone = item['phone']  # 以手机号为主键
            # 新记录：直接添加
            if phone not in result_dict: 
                result_dict[phone] = item
            # 已有记录：补充缺失字段
            else:
                # 身份证合并策略：保留首个有效记录
                if item['idcard'] and not result_dict[phone]['idcard']:
                    result_dict[phone]['idcard'] = item['idcard']
                # 银行卡合并策略：同上
                if item['bankcard'] and not result_dict[phone]['bankcard']:
                    result_dict[phone]['bankcard'] = item['bankcard']
    return pd.DataFrame(result_dict.values())  # 转换为DataFrame格式