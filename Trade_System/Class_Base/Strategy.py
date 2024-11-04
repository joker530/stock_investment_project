import time
from datetime import datetime
from multiprocessing import Queue
import numpy as np

import sys
import os

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

from Trade_System.Class_Base.Context import *
from utils.file_handing import *
from utils.date_handing import *

__all__ = ['Strategy']


# 编写一个策略类，这个策略类以函数作为参数进行输入，并有方法可以以Pickle的方式保存方便下次调取

class Strategy:
    def __init__(self, name, initialize=None, handle_data=None, on_event=None, before_trading_start=None,
                 after_trading_end=None, on_strategy_end=None, process_initialize=None,
                 after_code_change=None, unschedule_all=None):
        required_methods = [initialize, handle_data, on_strategy_end]
        if any(method is None for method in required_methods):
            raise TypeError('必需的方法未提供，请提供initialize、handle_data和on_strategy_end方法。')
        self.name = name
        self.initialize = initialize
        self.handle_data = handle_data
        self.on_event = on_event
        self.before_trading_start = before_trading_start
        self.after_trading_end = after_trading_end
        self.on_strategy_end = on_strategy_end
        self.process_initialize = process_initialize
        self.after_code_change = after_code_change
        self.unschedule_all = unschedule_all
        self.master = None

    def _beginning_of_trading_date(self, date):     # 需要在每个交易日执行之前调用一次，更新一下上下文的数据
        self.master.dt = long_datestr_to_dd(str(date))    # datetime.datetime这种格式，在回测框架的层面上进行递增,代表交易进行到的时间
        self.master.portfolio.update_date_info(date=date)

    def _ending_of_trading_date(self):
        # 需要在每个交易日结束并进行结算前调用一次
        self.master.portfolio.update_price_info()

    def _data_interaction_processing(self, update_queue: Queue, date: str):
        # 使用这个函数在每个交易日结束后进行必要的数据交互处理

        # 这里操作策略
        day_return = self.master.portfolio.returns  # 用这个计算目前的日收益率
        self.master.returns.append(day_return)
        new_seq = [x + 1 for x in self.master.returns]
        new_return = np.prod(new_seq)  # 每天获取当前回测下的总收益率

        # 这里操作基准
        new_benchmark_return = ((self.master.benchmark_dict[date] - self.master.benchmark_dict[self.master.date_range[0]])
                                / self.master.benchmark_dict[self.master.date_range[0]]) + 1
        self.master.benchmark_returns.append(new_benchmark_return)

        # 将新元素放入队列，这里放入的是收益率，还要再放入一个日期的,一次只放入一个
        update_queue.put((date, new_return, new_benchmark_return))

    def execute(self, context: Context, update_queue: Queue):  # 策略的执行函数, 这个队列用于进程中的通信
        self.master = context
        self.initialize(self.master)
        # 在这里对一些参数进行设置

        for date in self.master.date_range:

            self.before_trading_start(self.master)       # 注意这里必须只有一个context参数，其他的有也给我挤到context对象中
            self._beginning_of_trading_date(date)  # 更新这个对象内部的当前时间
            self.handle_data(self.master)
            self._ending_of_trading_date()         # 获取所有仓位当天的收盘价，更新仓位和账户价值信息的一个操作。
            self.after_trading_end(self.master)

            self._data_interaction_processing(update_queue=update_queue, date=date)
            time.sleep(0.1)

        self.on_strategy_end(self.master)
        time.sleep(0.5)

    def save(self):  # 策略对象的保存函数
        filename = 'Compressed_Strategy/' + self.name
        dump_class(filename, self)


if __name__ == "__main__":
    from Strategy_Functions.SVM import *
    from Trade_System.Class_Base.Context import *
    strategy = load_class('Compressed_Strategy/SVM')  # 由于这个脚本本身就存在Strategy这个类，所以加载时可以根据这个“blueprint”进行重建
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    date_format = "%Y-%m-%d"
    context = Context(cash=100000, start_date=start_date, end_date=end_date, kind='backtest', freq='daily',
                      strategy=strategy)
    context.save()
    # dump_class("context", context)
    del context
    context = load_class("Compressed_Context/context")
    pass
