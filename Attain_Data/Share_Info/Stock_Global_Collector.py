# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 22:55:55 2023

@author: Administrator
"""
##
import akshare as ak

# %%
__all__ = ['Stock_Global_Collector']

##
# %%
# 这个程序专门用于获得股票指数的数据
class Stock_Global_Collector():
    def get_sector_summary(self, symbol='当年', nianyue='202303'):
        df = ak.stock_szse_sector_summary(symbol=symbol, date=nianyue)
        self.sector_summary = df  # 获取各行业的交易量统计
        return df

    def get_st_datas(self):  # 获取st板块股票的实时数据
        df = ak.stock_zh_a_st_em()
        self.st_datas = df
        return df

    def get_IPO_benefits(self):  # 获取所有股票的投资信息（可能有IPO预期）
        df = ak.stock_ipo_benefit_ths()
        self.IPO_benefits = df
        return df

    def get_current_index_datas(self):  # 获取所有指数的实时行情
        df = ak.stock_zh_index_spot()
        self.index_current_datas = df
        return df

    def get_current_datas(self):  # 获取所有股票的实时行情
        df = ak.stock_sh_a_spot_em()
        self.current_datas = df
        return df

    def get_index_data(self, symbol="sz399552"):  # 获取指数一段时间的日K数据,从它的上市到当前
        df = ak.stock_zh_index_daily(symbol=symbol)  # 这个函数只有symbol这么一个参数
        self.index_data = df
        return df

    def get_index_data_period(self, symbol='000300', period='daily', start_date="20220101",
                              end_date="20230421"):  # 获取指数一段时间的日K数据
        df = ak.index_zh_a_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date)
        self.index_data = df
        return df

    def get_us_current_datas(self):  # 获取美股的实时行情
        df = ak.stock_us_spot_em()
        self.us_current_datas = df
        return df

    def get_AH_current_datas(self):  # 获取AH市场所用的行情数据
        df = ak.stock_zh_ah_spot()
        self.AH_current_datas = df
        return df

    def get_AH_dictionary(self):  # 获取AH股票字典
        df = ak.stock_zh_ah_name()
        self.AH_dictionary = df
        return df

    def get_us_stock_daily(self, code="BABA"):  # 获取美股日线数据
        df = ak.stock_us_zh_daily(symbol=code)
        self.us_stock_daily = df
        return df

    def get_department_research(self):  # 获取机构调研信息
        df = ak.stock_jgdy_tj_em(date="20210128")
        self.department_research = df
        return df

    def get_detail_department_research(self, date="20230428"):  # 获取机构调研详细信息
        df = ak.stock_jgdy_detail_em(date=date)
        self.detail_department_research = df
        return df

    def get_global_sy(self):  # 获取总体的商誉
        df = ak.stock_em_sy_profile()
        self.global_sy = df
        return df

    def get_jianzhi_report(self, symbol="沪市主板",
                           date="2019-12-31"):  # 商誉减值预期https://data.eastmoney.com/sy/yqlist.html
        df = ak.stock_em_sy_yq_list(symbol=symbol, trade_date="2019-12-31")
        self.jianzhi_report = df
        return df

    def get_sector_sy(self, date="2019-12-31"):  # 获取各行各业的商誉信息
        df = ak.stock_em_sy_hy_list(trade_date=date)
        self.sector_sy = df
        return df

    def get_account_statistic(self):
        df = ak.stock_account_statistics_em()
        self.account_statistic = df
        return df

    def get_analyst_rank_year(self, year='2023'):
        df = ak.stock_analyst_rank_em(year=year)
        self.analyst_rank_year = df
        return df

    def get_comments(self):  # 单次获取所有股评热度数据
        df = ak.stock_comment_em()
        self.comments = df
        return df
    # def get_board_rank(self,symbol=0,indicator=0):
    #  df=
