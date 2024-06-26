# -*- coding: utf-8 -*-
##
from datetime import datetime
import dateutil
import pandas as pd
import sys

sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform')
from Trade_System.Class_Base.Portfolio import *  # 导入总账户类
from Trade_System.Class_Base.Pickle import *  # 导入压缩方法
from Trade_System.Class_Base.RecommandIndex import *  # 导入策略评价类
##
__all__ = ["Context"]


# %% 上下文数据，定义了一个Context类和一个初始化的方法，主要存放具体笼统的信息
# context 对象主要用于管理回测参数和状态信息，例如设置股票池、回测时间范围等。
class Context:
    def __init__(self, cash, start_date, end_date, strategy, kind='backtest', freq='day'):
        # 总投入金额
        self.cash = cash
        # 开始时间
        self.start_date = start_date.strftime('%Y-%m-%d')
        # 结束时间
        self.end_date = end_date.strftime('%Y-%m-%d')
        # 运行的策略
        self._strategy = strategy
        # 持仓标的信息
        self.positions = {}
        # 基准
        self.benchmark = None
        # 股票池
        self.universe = None
        # 运行方式，一共有三种，分别是backtest、simtrade和livetrade，也就是回测、模拟交易和实时交易
        self.type = kind
        # 运行频率，一共有三种可选，分别是day、minute和tick
        self.freq = freq
        # 筛出在信息表中的日期
        trade_cal = pd.read_csv("D:/量化投资/交易框架的编写/trade_cal.csv")  # 读取这个数据表
        self.date_range = trade_cal[(trade_cal['trade_date'] >= str(self.start_date)) &
                                    (trade_cal['trade_date'] <= str(self.end_date))]['trade_date'].values
        # self.date_range = trade_cal[(trade_cal['is_open'] == 1) &
        # (trade_cal['cal_date'] >= str(self.start_date)) &
        # (trade_cal['cal_date'] <= str(self.end_date))]['cal_date'].values
        # 表示当前交易进行到的当前时间
        # 类似与datetime.datetime(2024, 6, 10, 0, 0)这种格式，在回测框架的层面上进行递增
        self.dt = dateutil.parser.parse(str(start_date))
        # 设置总账户，作为总体信息的一个总和，底下是子账户，所以要统计底下的子账户信息
        self.portfolio = Portfolio(self.cash)
        # 把外围类对象作为参数传递给内部类对象是合法的，传参进去该怎么样怎么样
        self.returns = list()  # 这个用于绘图的，一个交易频率过后往列表中添加一个元素，也用于回撤完成后的模型评价
        self.benchmark_returns = list()  # 这个的主要目的是与策略的回报率做一个参照
        self.recommand_index = RecommendIndex([],[],0.1)  # 这个在执行self._strategy.execute会再重新赋值一次

    def calculate_years_between_dates(self):  # 用这个函数将时间段转化为年数
        date_format = "%Y-%m-%d"
        date1 = datetime.strptime(self.start_date, date_format)  #
        date2 = datetime.strptime(self.end_date, date_format)
        # 计算日期之间的差异
        delta = date2 - date1
        # 将天数转换为年
        years_span = delta.days / 365.25  # 考虑闰年的影响，平均一年约为365.25天
        return years_span

    def execute_strategy(self, update_queue):
        self._strategy.execute(self, update_queue)  # 执行该策略类中的执行函数， 并把Context作为参数传进去
        years_span = self.calculate_years_between_dates()
        self.recommand_index = RecommendIndex(strategy_returns=self.returns, benchmark_returns=self.benchmark_returns,
                                              time_span=years_span)

    def __repr__(self):
        return f"Context(cash='{self.cash}', start_date='{self.start_date}', end_date='{self.end_date}', type='{self.type}', freq='{self.freq}', positions={self.positions}, benchmark={self.benchmark}, universe={self.universe})"


if __name__ == "__main__":
    strategy = load_class('Strategy_bags/SVM')
    start_date = '20220101'
    end_date = '20221231'
    date_format = "%Y-%m-%d"
    date1 = datetime.strptime(start_date, date_format)  #
    date2 = datetime.strptime(end_date, date_format)
    context = Context(cash=100000, start_date=date1, end_date=date2, kind='backtest', freq='daily',
                      strategy=strategy)
    dump_class("context", context)
    del context
    context = load_class("context")
