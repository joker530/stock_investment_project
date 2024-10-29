# -*- coding: utf-8 -*-
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

__all__ = ["G"]


# %% 设立全局变量G
# 主要用于记录回测框架下，目前的操作信息和各种设置，用户可以自己选择记录变量，并且在中断的时候不会消失
# 下单买卖等
class G:
    def __init__(self):
        self.security = []  # 设置起始股票池为空列表
        self.span = 1  # 默认的交易周期为1天
        self.trade_time = 0  # 用于记录回测的交易次数
        self.Type = "stock"  # 设置回测类型

    def set_all_stocks(self):  # 设置所有的A股上市股票为股票池
        pass
