# -*- coding: utf-8 -*-
"""
Created on Mon May  1 16:11:47 2023

@author: Administrator
"""
import pandas as pd

##
__all__ = ["Stock_Datas_Operator"]


##
# 这个函数专门编写对有若干股票代码的数据表的数据操作
class Stock_Datas_Operator():
    def __init__(self, df):  # 输入一个初始数据表
        self.df = df

    def get_certain_segment(self, lst=['6', '000', '002']):  # 从数据表中获得列表开头的股票及其信息，改变lst可以搜索不同交易所上市的股票
        pattern = '|'.join(lst) + '\d{3}'  # 其中6和000是主板；688和300是科创板和创业板；002是中小板
        df = self.df
        df_keys = df.keys()
        df = df[df[df_keys[1]].str.match(pattern)]  # 一般第二个就是“股票代码”或者“代码”
        self.df = df
        return df

    def select_quality_bigger(self, string: str, index):
        df = self.df
        than_index = df[string] >= index
        result = df[than_index]
        self.df = result
        return self.df

    def select_quality_smaller(self, string: str, index):
        df = self.df
        less_index = df[string] < index
        result = df[less_index]
        self.df = result
        return self.df

    def select_quality_interval(self, string: str, index1, index2):
        df = self.df
        mid_index = (df[string] < index2) & (df[string] >= index1)
        result = df[mid_index]
        self.df = result
        return self.df


## 测试
import akshare as ak
if __name__ == "__main__":
    df = ak.stock_sz_a_spot_em()
    sdo = Stock_Datas_Operator(df)
    new_df = sdo.get_certain_segment()
    new_df = sdo.select_quality_interval('换手率', 0.5, 2)
    new_df = sdo.select_quality_bigger('涨跌幅', 1)
