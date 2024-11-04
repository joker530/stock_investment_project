# -*- coding: utf-8 -*-
"""
Created on Mon May  1 11:08:44 2023

@author: Administrator
"""
# %%
import sys

sys.path.append('/Datasets/Data_Table/Industry_Datas')
import akshare as ak
import pandas as pd
import os
import chardet

__all__ = ["Industry"]


# %%
# 这个类专门用来获取行业的信息和指标
class Industry():
    def __init__(self):
        pass

    def get_industry_sectors(self):
        try:
            file_path = os.path.join(os.getcwd(),
                                     "/Datasets/Data_Table/Industry_Datas/Industry_Sectors/industry_sectors.csv")
            with open(file_path, 'rb') as f:
                content = f.read()
                encoding = chardet.detect(content)['encoding']
                df = pd.read_csv(file_path, encoding=encoding)
        except FileNotFoundError:
            df = ak.stock_board_industry_name_em()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path, index=False, encoding='utf-8')
        self.industry_sectors = df
        return df

    def get_industry_stocks(self, industry='小金属'):
        self.industry = industry
        try:
            file_path = os.path.join(os.getcwd(),
                                     "D:/量化投资/交易框架的编写/backtesting_platform/Data_Table/Industry_Datas/Industry_Stocks/{}.csv".format(
                                         industry))
            with open(file_path, 'rb') as f:
                content = f.read()
                encoding = chardet.detect(content)['encoding']
                df = pd.read_csv(file_path, encoding=encoding)
        except FileNotFoundError:
            df = ak.stock_board_industry_cons_em(symbol=industry)
            df['代码'] = df['代码'].astype(str).str.zfill(6)  # 补零为6位
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path, index=False, encoding='utf-8')
        self.industry_stocks = df

    def get_all_industry_stocks(self):
        industries = self.get_industry_sectors()['板块名称']
        for i in range(len(industries)):
            self.get_industry_stocks(industry=industries[i])
