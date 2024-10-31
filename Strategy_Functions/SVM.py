import sys
import os

Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)

from Attain_Data.Share_Info import *  # 导入数据获取方法
from Trade_System.Class_Base import *  # 导入交易相关的类
import datetime

__all__ = ['class_init', 'initialize', 'handle_data', 'on_event', 'before_trading_start', 'after_trading_end',
           'on_strategy_end', 'process_initialize', 'after_code_change', 'unschedule_all', 'serialize_g',
           'signal_handler']

'在这里说明这是一个什么样的策略，它的实现思路是怎样的。'

def class_init(strategy, cash=100000, start_date='20220101', end_date='20230503', freq="day"):
    # 更新交易数据表
    # sic = Stock_Info_Collector()   # 必要时再更新交易日表
    # sic.get_trade_date()  # 更新交易日表,到今年的最后一天为止
    context = Context(cash, start_date, end_date, freq=freq, strategy=strategy)

    return context


# %%
def initialize(context: Context):  # 初始化函数
    cash = context.cash
    context.portfolio.create_new_SubPortfolio(inout_cash=cash, margin=1, type='stock', name="我的股票账户1")  # 创建一个子账户

    pass


def handle_data(context: Context, date):  # 运行策略
    pass


def on_event():  # 事件回调函数
    pass


def before_trading_start(context: Context, date):  # 开盘前运行的策略代码
    # 这里需要在每个交易日开盘前对账户的一些有关于时间的参数做一个新的设定


    pass


def after_trading_end(context: Context, date):  # 收盘后运行策略
    pass


def on_strategy_end(context: Context):  # 策略运行完后调用
    pass


def process_initialize(context: Context):  # 每次回测或模拟盘重启后调用，用于初始化一些不能被pickle序列保存的变量
    pass


def after_code_change(context: Context):  # 模拟交易更换代码后运行函数,主要用于模拟盘
    pass


def unschedule_all(context: Context):  # 取消所有定时运行，主要用于模拟盘，回测不需要，运行后可以又设置运行频率
    pass


def serialize_g(context, g):  # 发生中断时保存这两个全局变量
    dump_class('Context', context)
    dump_class('g', g)
    print("Serialized global data successfully.")


def signal_handler(sig, frame, context, g):
    print('You pressed Ctrl+C!')  # 键盘终止时调用该函数进行保存
    serialize_g(context, g)
    sys.exit(0)  # 终止程序，并返回0给操作系统
