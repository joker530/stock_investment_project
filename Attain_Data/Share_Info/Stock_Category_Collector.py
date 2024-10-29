# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 21:15:57 2023

@author: Administrator
"""
import akshare as ak

# %%
__all__ = ["Stock_Category_Collector"]


# %%
# 这个脚本用来获取分类股票的数据信息
class Stock_Category_Collector():
    def __init__(self):
        pass

    def get_st_datas(self):  # 获取st板块股票的实时数据
        df = ak.stock_zh_a_st_em()
        self.st_datas = df
        return df

    def get_IPO_benefits(self):  # 获取所有股票的投资信息（可能有IPO预期）
        df = ak.stock_ipo_benefit_ths()
        self.IPO_benefits = df
        return df

    def get_new_stocks(self):  # 获取次新股最近一个交易日的数据
        df = ak.stock_zh_a_new()
        self.new_stocks = df
        return df

    def get_stop_stocks(self):  # 获取退市的股票数据
        df = ak.stock_zh_a_stop_em()
        self.stop_stocks = df
        return df

    def get_tech_stocks(self):  # 获取科技股的即时行情数据
        df = ak.stock_zh_kcb_spot()
        self.tech_stocks = df
        return df

    def get_tech_report(self):  # 获取科创板的报告数据
        df = ak.stock_zh_kcb_report_em(from_page=1, to_page=100)
        self.tech_report = df
        return df

    def get_Ga_current_datas(self):  # 获取中概股的行情数据
        df = ak.stock_us_zh_spot()
        self.Ga_current_datas = df
        return df

    def get_hsgt_flow_summary(self):  # 获取沪深港通资金的流向
        df = ak.stock_hsgt_fund_flow_summary_em()
        self.hsgt_flow_summary = df
        return df

    def get_hk_components(self):  # 获取港股通成分股
        df = ak.stock_hk_ggt_components_em()
        self.hk_components = df
        return df

    def get_north_flow(self, symbol="沪股通"):  # 获取北向资金净流入数据，单位万元，包含当日成交净买额和当日买入申报未成交金额;
        df = ak.stock_hsgt_north_net_flow_in_em(symbol=symbol)
        self.north_flow = df
        return df

    def get_north_cash(self, symbol="沪股通"):  # 获取北向资金的余额
        df = ak.stock_hsgt_north_cash_em(symbol=symbol)
        self.north_cash = df
        return df
