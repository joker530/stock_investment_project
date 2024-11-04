# 这个函数专门用于写序列的处理的函数
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)

__all__ = ["get_series_changes_series"]


##
def get_series_changes_series(series: list) -> list:
    # 初始化涨跌幅度列表，第一天的涨跌幅度为0
    daily_changes = [0]

    # 遍历价格列表，从第二天开始
    for i in range(1, len(series)):
        # 计算涨跌幅度
        change = (series[i] - series[i - 1]) / series[i - 1]
        daily_changes.append(change)

    return daily_changes
