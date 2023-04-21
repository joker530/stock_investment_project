# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 21:01:39 2023

@author: Administrator
"""
# 这个程序用来建立股票交易框架，这里先假设有一个股票账户 SubPortfolio
# 我可以在这个股票账户对象中进行任意的操作以达到我的目的
import sys
sys.path.append('G:/ai/量化投资/交易框架的编写/backtesting_platform/muti_classes')
import muti_classes as mc
from tushare_frame import ts_pro,ts_trade_cal
from datetime import datetime,timedelta,date
# %%
class stock_account():
    def __init__(self, inout_cash:float, margin=1):
        self.account=mc.SubPortfolio(inout_cash,margin)  #生成一个账户对象
    def update_cal(self, exchange="SSE", start_date="20100101"):
        today=date.today()
        end_date = today.strftime("%Y%m%d")
        ts_trade_cal(exchange, start_date, end_date)  #交易日数据库得到跟新
    # 获取某一只股票的日、周、月线数据
    def get_Kline_datas(code:str,period:str,start_date="20220101",end_date="20230421",adjust=None):
        df=stock_zh_a_hist(code,period,start_date,end_date,adjust)
    