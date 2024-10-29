# -*- coding: utf-8 -*-
"""
Created on Wed May  3 10:34:55 2023

@author: Administrator
"""
##
# 说明
# 这个函数是回测框架的主函数，它的内部调用了其它定义的函数
# ，同时在执行框架函数前，会预先定义一些基础的对象
# 在新建策略的开头导入该脚本框架，并且可以对这些函数进行重新定义以定制使用方法
# 导入方法 import Backtesting_Structure,
# %% 导入必要的库
import sys

sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform')
import signal
from Strategy_Functions.ExecutiveBase.Stock_Executive.SVM import *  # 导入对应的策略函数
from Trade_System.Class_Base.Strategy import *
from Trade_System.Class_Base.G import *

##
# %% 先实现在唯一一个账户，而且只能做多的情况下设计交易框架


# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    strategy = Strategy(name='SVM', initialize=initialize, handle_data=handle_data,
                        before_trading_start=before_trading_start, after_trading_end=after_trading_end,
                        on_strategy_end=on_strategy_end)
    strategy.save()
    context = class_init(strategy=strategy)
    g = G()
    context.execute_strategy()

