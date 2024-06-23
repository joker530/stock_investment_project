import time

from Trade_System.Class_Base.Pickle import *
from Trade_System.Class_Base.Context import *
from datetime import datetime
from multiprocessing import Queue

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

    def execute(self, context: Context, update_queue: Queue):  # 策略的执行函数, 这个队列用于进程中的通信
        self.initialize(context)   #
        new_return = 0
        for date in context.date_range:
            context.dt = datetime.strptime(date, '%Y-%m-%d').date()  # 每次变化时间，最后的格式类似datetime.date(1990, 1, 1)
            context.portfolio.current_trade_date = context.dt
            self.before_trading_start(context, date)
            self.handle_data(context, date)
            self.after_trading_end(context, date)
            # 这里还需要有一个获取当天的收盘价，更新仓位和账户价值信息的一个操作。
            new_return += 1
            context.returns.append(new_return)
            update_queue.put((date, new_return))   # 将新元素放入队列，这里放入的是收益率，还要再放入一个日期的
            # print(update_queue.qsize())
            time.sleep(0.1)
        self.on_strategy_end(context)
        time.sleep(0.5)

    def save(self):  # 策略对象的保存函数
        filename = 'Strategy_bags/' + self.name
        dump_class(filename, self)
