# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 09:11:35 2023

@author: Administrator
"""
import sys

sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform')
from datetime import datetime, timedelta
from Trade_System.Class_Base.Context import *
from Trade_System.Class_Base.G import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import tushare as ts
import dateutil
import akshare as ak


# %%  设置token初始化pro接口
# 设置token初始化pro接口(Tushare)
def ts_pro():
    # 设置token
    # tushare官网:https://tushare.pro/register?reg=462261
    # 注册账户，就有了你的token，登录后个人主页中找
    ts.set_token('3bbe7964d6b047f09e9f622ded0cabf05bf2b187d25609e1d1fabb94')
    # 初始化pro接口
    pro = ts.pro_api()
    return pro


# %% 获取各大交易所交易日历数据,默认提取的是上交所(Tushare)
def ts_trade_cal(exchange, start_date, end_date):
    pro = ts_pro()
    # 获取各大交易所交易日历数据,默认提取的是上交所
    """
        输入参数
        名称    类型    必选    描述
        exchange    str    N    交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源
        start_date    str    N    开始日期 （格式：YYYYMMDD 下同）
        end_date    str    N    结束日期
        is_open    str    N    是否交易 '0'休市 '1'交易

        输出参数
        名称    类型    默认显示    描述
        exchange    str    Y    交易所 SSE上交所 SZSE深交所
        cal_date    str    Y    日历日期
        is_open    str    Y    是否交易 0休市 1交易
        pretrade_date    str    Y    上一个交易日
    """
    df = pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date)
    # 按'cal_date'排序
    df.sort_values('cal_date', inplace=True)
    # 转换为日期格式
    df['cal_date'] = pd.to_datetime(df['cal_date'])
    # 设置'cal_date'为索引
    df.set_index('cal_date', inplace=True)
    # 存储为csv文件
    df.to_csv('G:\\ai\\量化投资\\交易框架的编写\\trade_cal.csv')


# start_date='20220101'
# end_date='20230405'
# ts_trade_cal('SSE', start_date, end_date)
# %%
# A股日线行情(Tushare)
def ts_daily(security, start_date, end_date, fields=('open', 'close', 'high', 'low', 'vol')):
    pro = ts_pro()
    # A股日线行情(Tushare)
    """
        输入参数
        名称    类型    必选    描述
        ts_code    str    N    股票代码（支持多个股票同时提取，逗号分隔）
        trade_date    str    N    交易日期（YYYYMMDD）
        start_date    str    N    开始日期(YYYYMMDD)
        end_date    str    N    结束日期(YYYYMMDD)

        输出参数
        名称    类型    描述
        ts_code    str    股票代码
        trade_date    str    交易日期
        open    float    开盘价
        high    float    最高价
        low    float    最低价
        close    float    收盘价
        pre_close    float    昨收价(前复权)
        change    float    涨跌额
        pct_chg    float    涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
        vol    float    成交量 （手）
        amount    float    成交额 （千元）
    """
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')
    df = pro.daily(ts_code=security, start_date=start_date, end_date=end_date)
    df.sort_values('trade_date', inplace=True)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    df.to_csv('G:\\ai\\量化投资\\交易框架的编写\\datas\{}.csv'.format(security))
    # 读取csv文件
    df = pd.read_csv('G:\\ai\\量化投资\\交易框架的编写\\datas\{}.csv'.format(security),
                     index_col='trade_date', parse_dates=['trade_date'])
    # 截取start_date:end_date段数据
    df = df.loc[start_date:end_date, :]
    return df[list(fields)]


# start_date='20200101'
# end_date='20230405'
# security='601127.SH'
# ts_daily(security, start_date, end_date)
# %% 实例化对象函数
def generate_example(cash, start_date, end_date, trade_cal):
    g = G()
    context = Context(cash, start_date, end_date, trade_cal)
    return g, context


# %% 初始化函数，设置基准等等
def initialize(g, context, security, bench):
    # 设定002624作为基准
    set_bench_mark(bench, context)
    # 5日均线全局参数
    g.ma1 = 5
    # 30日均线全局参数
    g.ma2 = 30
    # 要操作的股票601127
    g.security = security
    # 初始化资金量和起始日期


# %%设置基准，这里设置单个股票为基准
# 如果像聚宽那样设置沪深300为基准
# 比较麻烦
# 代码量多
# 这里就设置单个股票为基准
def set_bench_mark(security, context):
    context.benchmark = security


# %% 设置context对象的股票池universe
def set_universe(lst, context):  # 输入一个包含各种股票池的列表
    context.universe = lst


# %%在一段时间的历史交易日中，获取历史数据
def attribute_history(security, count, trade_cal, context, fields=('open', 'close', 'high', 'low', 'vol')):
    end_date = (context.dt - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = trade_cal[(trade_cal['is_open'] == 1) & (trade_cal['cal_date'] <= str(end_date))][-count:].iloc[0, :][
        'cal_date']
    return attribute_daterange_history(security, start_date, end_date, fields)


# df3=attribute_history('002624.SZ',10,trade_cal)
# %% 输入股票代码、起止时间和搜索域来，获取历史数据基础函数
def attribute_daterange_history(security, start_date, end_date,
                                fields=('open', 'close', 'high', 'low', 'vol')):  # vol是成交量的意思，以手为单位
    # 尝试读取本地数据
    try:
        f = open('G:\\ai\\量化投资\\交易框架的编写\\datas\{}.csv'.format(security))  # 打开数据文件
        df = pd.read_csv(f, index_col='trade_date', parse_dates=['trade_date'])  # 以交易日期作为index
        if ((start_date <= str(df.index[-1])) & (start_date >= str(df.index[0])) & (end_date <= str(df.index[-1])) & (
                end_date >= str(df.index[0]))):
            df = df.loc[start_date:end_date, :]  # 截取其中的一段交易日的各种数据赋值给df数据表
        else:
            df = ts_daily(security, start_date, end_date)  # 重新下载获取
    # 如果没有本地数据就下载
    except FileNotFoundError:
        # 2022-10-18 转换为 20221018
        # time_array1 = time.strptime(start_date, '%Y-%m-%d')
        # start_date = time.strftime('%Y%m%d', time_array1)
        # time_array2 = time.strptime(end_date, '%Y-%m-%d')
        # end_date = time.strftime('%Y%m%d', time_array2)
        df = ts_daily(security, start_date, end_date)
    except:
        df = ts_daily(security, start_date, end_date)  # 重新下载获取
    return df[list(fields)]


# df1=attribute_daterange_history('002624.SZ','20200101','20230405')
# df2=attribute_daterange_history('601127.SH', '20200101','20230405')
# %% 输入股票代码，获得今天日线行情
def get_today_data(security, context):
    today = context.dt.strftime('%Y/%m/%d')
    # 尝试读取本地数据
    try:
        f = open('G:\\ai\\量化投资\\交易框架的编写\\datas\{}.csv'.format(security), 'r')
        data = pd.read_csv(f, index_col='trade_date', parse_dates=['trade_date']).loc[today, :]
    # 如果没有本地数据就下载
    except FileNotFoundError:
        pro = ts_pro()
        time_array = time.strptime(today, '%Y-%m-%d')
        today = time.strftime('%Y%m%d', time_array)
        data = pro.daily(ts_code=security, start_date=today, end_date=today).loc[0, :]
    # 停牌返回空数据
    except KeyError:
        data = pd.Series()
    return data


# data=get_today_data('603039.SH',context)
# %% 买卖订单基础函数,输入股票代码和下单的股数
def order_num(security, amount, context):
    # 股票价格
    today_data = get_today_data(security, context)  # 先获得最近的一个交易日的数据
    p = today_data['open']  # 获取其今日的开盘价
    # 停牌
    if len(today_data) == 0:
        print("今日停牌")
        return
    # 现金不足
    if context.cash - amount * p < 0:
        amount = int(context.cash / p / 100) * 100
        print("现金不足,已调整为%d" % amount)  # 将所有剩下的钱买入股票
    # 100的倍数
    if amount % 100 != 0:  # 如果买入的股数除以100有余数
        if amount != -context.positions.get(security, 0):  # 这个存在是在考虑分红送股的情况，可能持有的数量不是100的倍数，可以全部抛出
            amount = int(amount / 100) * 100  # int相当于取ceil(),调整amount的数量
            print("不是100的倍数,已调整为%d" % amount)
    # 卖出数量超过持仓数量
    if context.positions.get(security, 0) < -amount:  # 卖出此时amount为负数
        amount = -context.positions.get(security, 0)
        print("卖出数量不能超过持仓数量,已调整为%d" % amount)  # 卖出的股票数量超过持仓数量，则全仓抛出
    # 将买卖股票数量存入持仓标的信息
    context.positions[security] = context.positions.get(security, 0) + amount
    # 剩余资金
    context.cash -= amount * p
    # 如果一只股票持仓为0，则删除上下文数据持仓标的信息中该股信息
    if context.positions[security] == 0:
        del context.positions[security]


# %% 目标股数下单
def order_target(security, amount, context):
    if amount < 0:
        print("数量不能为负，已调整为0")
        amount = 0
    hold_amount = context.positions.get(security, 0)  # 获得已经持有的股数
    delta_amount = amount - hold_amount  # 离目标股数的股数差距，故会根据你现在持有的股数来决定应该购买的股数
    order_num(security, delta_amount)  # 执行下单


# %% 目标价值下单
def order_value(security, value, context):
    today_data = get_today_data(security, context)
    if (today_data.empty) == False:  # 不停牌时才操作
        amount = int(value / today_data['open'])
        order_num(security, amount, context)


# %% 目标价值下单
def order_target_value(security, value, context):
    if value < 0:
        print("价值不能为负，已调整为0")
        value = 0  # 目标价值取0
    today_data = get_today_data(security, context)
    if (today_data.empty) == False:
        # 处理 today_data 为空的情况,停牌了啥也操作不了
        hold_value = context.positions.get(security, 0) * today_data['open']
        delta_value = value - hold_value
        order_value(security, delta_value, context)


# %% 筛选股票函数
# 按指数成分进行筛选，给出指数代码，筛选成分股
def set_index_stock():
    pro = ts_pro()
    df = pro.index_weight(index_code='399300.SZ', start_date='20180901', end_date='20180930')
    return df
# df=set_index_stock()
# print(df)
