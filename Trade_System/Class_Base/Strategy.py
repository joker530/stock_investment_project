import time
from datetime import datetime
from multiprocessing import Queue
import akshare as ak

import sys
import os

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

from utils.file_handing import *
from Trade_System.Class_Base.Context import *

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

    def _get_benchmark_returns(self, context:Context):  # 用这个函数专门得到基准在回测区间的日收益率序列
        start_date = context.date_range[0].replace('-', '')
        end_date = context.date_range[-1].replace('-', '')
        benchmark_code = context.benchmark.split()[1]  # 获取基准的代码，如"sh000300"
        stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol=benchmark_code, start_date=start_date,
                                                                end_date=end_date)  # 每次调用API只获取一天的数据
        close_list = stock_zh_index_daily_em_df['close']  # 获取表中的收盘价
        pass

    def execute(self, context: Context, update_queue: Queue):  # 策略的执行函数, 这个队列用于进程中的通信
        self.initialize(context)  # 在这里对一些参数进行设置
        last_return = 0  # 用这个变量记录前一个交易日回测下的历史收益率
        # 这里在开始回测之前，直接获取benchmark在start_date到end_date的数据
        for date in context.date_range:
            context.dt = datetime.strptime(date, '%Y-%m-%d').date()  # 每次变化时间，最后的格式类似datetime.date(1990, 1, 1)
            context.beginning_of_trading_date(date)  # 更新这个对象内部的当前时间
            # context.portfolio.current_trade_date = context.dt   #  这里要修改
            self.before_trading_start(context)   # 注意这里必须只有一个context参数，其他的有也给我挤到context对象中
            self.handle_data(context)
            self.after_trading_end(context)
            # 这里还需要有一个获取当天的收盘价，更新仓位和账户价值信息的一个操作。
            # 这里操作策略
            new_return = context.portfolio.returns  # 每天获取当前回测下的历史收益率
            day_return = (new_return - last_return) / (last_return + 1 + 1e-9)  # 用这个计算当日收益率
            context.returns.append(day_return)

            # 这里操作基准
            benchmark_code = context.benchmark.split()[1]  # 获取基准的代码，如"sh000300"
            date_space = date.replace('-', '')  # 对字符串进行一次变换
            stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol=benchmark_code, start_date=date_space,
                                                                    end_date=date_space)  # 每次调用API只获取一天的数据

            update_queue.put((date, new_return))  # 将新元素放入队列，这里放入的是收益率，还要再放入一个日期的,一次只放入一个
            last_return = new_return
            # print(update_queue.qsize())
            time.sleep(0.1)
        self.on_strategy_end(context)
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
