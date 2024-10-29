# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 21:01:39 2023

@author: Administrator
"""
# 这个程序用来建立股票交易框架，这里先假设有一个股票账户 SubPortfolio
# 我可以在这个股票账户对象中进行任意的操作以达到我的目的
import sys

sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform/Attain_Data/Share_Info')
from datetime import datetime, timedelta, date
import akshare as ak

# %%
__all__ = ['Stock_Info_Collector']

# %% 定义股票账户的查找方式，里面包含着各种数据的查找
class Stock_Info_Collector():  # 包含一个SubPortfolio对象和方法
    def __init__(self, code="601127.SH"):  # 这里输入的形如数字“601127”,针对单一代码的查询器
        part1,part2 = code.split('.')
        self.code = part1
        self.code1 = code
        self.code2 = part2.lower() + part1   # 这里先把大写的字符串变成小写
        self.code3 = part2 + part1   # 这里的保持大写
        today = date.today()
        self.today = today.strftime("%Y%m%d")

    def get_trade_date(self):
        trade_date = ak.tool_trade_date_hist_sina()
        self.trade_date = trade_date
        trade_date.to_csv("D:/量化投资/交易框架的编写/trade_cal.csv")  # 重新更新该数据表
        # return trade_dateS

    # 获取某一只股票的日、周、月线数据
    def get_Kline_datas(self, period: str, start_date="20220101", end_date="20230421", adjust="qfq", Code=".SH"):
        df = ak.stock_zh_a_hist(self.code, period, start_date, end_date, adjust)
        self.KL = df
        self.Code = self.code + Code
        df.to_csv('D:/量化投资/交易框架的编写/backtesting_platform/Data_Table/datas_daily/{}.csv'.format(self.Code))
        return df  # 输出的df是这种格式[日期，股票代码，开盘，收盘，最高，最低，成交量，成交额，振幅，涨跌额，换手率]

    def get_individual_info(self):  # 获取一只股票的基本信息
        df = ak.stock_individual_info_em(self.code)
        self.individual_info = df
        return df

    def get_baojia(self):  # 获取买五到卖五的报价
        df = ak.stock_bid_ask_em(self.code)
        self.baojia = df
        return df

    def get_current_datas(self):  # 获取单只股票的实时行情
        df = ak.stock_sh_a_spot_em()
        df = df.loc[df['代码'] == self.code]
        self.current_datas = df
        return df

    def get_fenbi_data(self, trade_date="20230421"):
        df = ak.stock_zh_a_tick_tx(symbol=self.code2, trade_date=trade_date)
        self.fenbi = df  # 获取某一日的各时段的成交具体详情,标有买盘和卖盘
        return df

    def get_tech_daily_history(self):  # 这个函数用于获取科创板的数据，输入的股票一定要是科创板的
        df = ak.stock_zh_kcb_daily(symbol=self.code2, adjust="hfq")
        self.tech_daily_history = df
        return df

    def get_zyjs(self):
        df = ak.stock_zyjs_ths(symbol=self.code)
        self.zyjs = df
        return df

    def get_zygc(self):
        df = ak.stock_zygc_ym(symbol=self.code)
        self.zygc = df
        return df

    def get_gpzy_ratio(self, date="20220408"):  # 获得上市公司质押比数据
        df = ak.stock_gpzy_pledge_ratio_em(date=date)
        self.gpzy_ratio = df
        return df

    def get_analyst_detail(self, analyst_id="11000257131",
                           indicator="最新跟踪成分股"):  # 从 {"最新跟踪成分股", "历史跟踪成分股", "历史指数"} 中选择一个
        df = ak.stock_analyst_detail_em(analyst_id=analyst_id, indicator=indicator)
        self.analyst_detail = df     # 这个是获取分析师的
        return df

    def get_comments_detail(self):  # 获取个股的机构控盘信息
        df = ak.stock_comment_detail_zlkp_jgcyd_em(symbol=self.code)
        self.comments_detail = df
        return df

    def get_zhpj_comments_detail(self):  # 东方财富上对个股的综合评分
        df = ak.stock_comment_detail_zhpj_lspf_em(symbol=self.code)
        self.zhpj_comments_detail = df
        return df

    def get_focus_comments(self):  # 东方财富网上的市场热度
        df = ak.stock_comment_detail_scrd_focus_em(symbol=self.code)
        self.focus_comments = df
        return df

    def get_desire_current_comments(self):  # 东方财富网上的市场参与意愿
        df = ak.stock_comment_detail_scrd_desire_em(symbol=self.code)
        self.desire_comments = df
        return df

    def get_desire_daily_comments(self):  # 日交易参与意愿
        df = ak.stock_comment_detail_scrd_desire_daily_em(symbol=self.code)
        self.desire_daily_comments = df
        return df

    def get_average_cost(self):  # 获取目前的市场成本
        df = ak.stock_comment_detail_scrd_cost_em(symbol=self.code)
        self.average_cost = df
        return df

    def get_minute_datas_one(self, period="1"):  # 获取分时数据，分钟级别,对于分粥级别额数据只有半个月的时长
        df = ak.stock_zh_a_minute(symbol=self.code2, period=period, adjust="qfq")
        self.minute_dates1=df
        return df
    
    def get_minute_datas_two(self, start_date="2021-01-01 09:32:00", end_date="2021-09-06 09:32:00", period='1', adjust="hfq"):
        df = ak.stock_zh_a_hist_min_em(symbol=self.code, start_date=start_date, end_date=end_date, period=period, adjust=adjust)
        self.minute_dates2=df
        return df