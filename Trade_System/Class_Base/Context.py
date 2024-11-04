# -*- coding: utf-8 -*-
##
from datetime import datetime
import pandas as pd

import sys
import os

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)
##
from Trade_System.Class_Base.Portfolio import *  # 导入总账户类
from Trade_System.Class_Base.RecommandIndex import *  # 导入策略评价类
from Attain_Data.Share_Info.Stock_Global_Collector import *  # 导入指数数据获取对象
from utils.file_handing import *  # 导入文件处理工具
from utils.date_handing import *  # 导入日期格式处理工具
from utils.series_handing import *
##
__all__ = ["Context"]


# %% 上下文数据，定义了一个Context类和一个初始化的方法，主要存放具体笼统的信息
# context 对象主要用于管理回测参数和状态信息，例如设置股票池、回测时间范围等。
class Context:
    def __init__(self, cash, start_date: datetime, end_date: datetime, strategy, benchmark=None,
                 kind='backtest', freq='daily'):
        # 总投入金额
        self.cash = cash
        # 开始时间
        self.start_date = dd_to_long_datestr(start_date)  # 转换为字符串的形式
        # 结束时间
        self.end_date = dd_to_long_datestr(end_date)
        # 间隔年数
        self.years_span = None
        # 运行的策略
        self._strategy = strategy
        # 持仓标的信息
        self.positions = {}
        # 基准
        self.benchmark = benchmark
        self.benchmark_dict = None
        # 股票池
        self.universe = None
        # 运行方式，一共有三种，分别是backtest、simtrade和livetrade，也就是回测、模拟交易和实时交易
        self.type = kind
        # 运行频率，一共有三种可选，分别是daily、weekly和mouthly
        self.freq = freq
        # 筛出在信息表中的日期
        trade_cal = pd.read_csv(Base_dir + '/Datasets/Data_Table/Trading_Timetable/' + 'stock_trade_cal.csv')  # 读取这个数据表
        self.date_range = get_date_range_list(trade_cal_csv=trade_cal, start_date=self.start_date, end_date=self.end_date)

        # 设置总账户，作为总体信息的一个总和，底下是子账户，所以要统计底下的子账户信息
        self.portfolio = Portfolio(self.cash)
        # 把外围类对象作为参数传递给内部类对象是合法的，传参进去该怎么样怎么样
        self.returns = list()  # 这个用于绘图的，一个交易频率过后往列表中添加一个元素，也用于回撤完成后的模型评价
        self.benchmark_returns = list()  # 这个的主要目的是与策略的回报率做一个参照
        self.recommand_index = RecommendIndex([], [], 0.1)  # 这个在执行self._strategy.execute会再重新赋值一次

    def calculate_years_between_dates(self) -> float:  # 用这个函数将时间段转化为年数
        date_format = "%Y-%m-%d"
        date1 = datetime.strptime(self.start_date, date_format)  # 转换为datetime的对象
        date2 = datetime.strptime(self.end_date, date_format)
        # 计算日期之间的差异
        delta = date2 - date1
        # 将天数转换为年
        years_span = delta.days / 365.25  # 考虑闰年的影响，平均一年约为365.25天
        return years_span

    def benchmark_calculation(self) -> dict:  # 用这个函数计算基准在一段时间的序列，并返回序列数据
        if self.benchmark is None:
            raise TypeError("请在策略文件中设置基准后再进行基准计算!")
        else:
            keys = list(self.benchmark.keys())
            values = list(self.benchmark.values())
            sgc = Stock_Global_Collector()
            start_date = long_to_short_datestr(self.start_date)
            end_date = long_to_short_datestr(self.end_date)
            final_dict = {}
            for i in range(len(self.benchmark)):
                df = sgc.get_index_data_period(symbol=keys[i], period=self.freq, start_date=start_date, end_date=end_date)
                df.set_index("日期", inplace=True)
                temp_dict = (df["收盘"]*values[i]).astype(float).to_dict()
                for key, value in temp_dict.items():
                    if key in final_dict:
                        final_dict[key] += value
                    else:
                        final_dict[key] = value
            return final_dict

    def execute_strategy(self, update_queue):
        self.portfolio.create_new_SubPortfolio(mother_cash=self.portfolio.remaining_recharge, name="account1")
        # 创建一个子账户
        self.benchmark_dict = self.benchmark_calculation()
        self.years_span = self.calculate_years_between_dates()

        self._strategy.execute(self, update_queue)  # 执行该策略类中的执行函数， 并把Context作为参数传进去
        self.benchmark_returns = get_series_changes_series(self.benchmark_returns)

        self.recommand_index = RecommendIndex(strategy_returns=self.returns, benchmark_returns=self.benchmark_returns,
                                              time_span=self.years_span)

    def save(self):  # 策略对象的保存函数
        filename = 'Compressed_Context/' + 'Context'
        dump_class(filename, self)

    def __repr__(self):
        return f"Context(cash='{self.cash}', start_date='{self.start_date}', end_date='{self.end_date}', type='{self.type}', freq='{self.freq}', positions={self.positions}, benchmark={self.benchmark}, universe={self.universe})"
