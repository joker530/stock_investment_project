# -*- coding: utf-8 -*-
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

__all__ = ["SecurityUnitData"]


# %%  用于存储某一标的在某一段时间内的情况，可以考接口进行生成
class SecurityUnitData:
    def __init__(self, capitalization, turnover_ratio, market_unit, circulating_capitalization, total_capitalization,
                 close_price, volume, date):
        self.capitalization = capitalization  # 股票流通股本
        self.turnover_ratio = turnover_ratio  # 股票周转率
        self.market_unit = market_unit  # 当前股票的市场单位
        self.circulating_capitalization = circulating_capitalization  # 流通市值，单位为元
        self.total_capitalization = total_capitalization  # 总市值，单位为元
        self.close_price = close_price  # 收盘价，单位为元
        self.volume = volume  # 成交价，单位为股
        self.date = date  # 日期，类如20230705

    def to_dict(self):  # 返回一个包含这个类所有信息的一个字典
        return {
            'capitalization': self.capitalization,
            'turnover_ratio': self.turnover_ratio,
            'market_unit': self.market_unit,
            'circulating_capitalization': self.circulating_capitalization,
            'total_capitalization': self.total_capitalization,
            'close_price': self.close_price,
            'volume': self.volume,
            'date': self.date
        }

    def to_df(self):  # 输出一个数据表
        import pandas as pd
        return pd.DataFrame([self.to_dict()])

    def show(self):  # 打印这个类的所有信息
        print("SecurityUnitData:\n")
        print(f"  Date: {self.date}")
        print(f"  Capitalization: {self.capitalization}")
        print(f"  Turnover Ratio: {self.turnover_ratio}")
        print(f"  Market Unit: {self.market_unit}")
        print(f"  Circulating Capitalization: {self.circulating_capitalization}")
        print(f"  Total Capitalization: {self.total_capitalization}")
        print(f"  Close Price: {self.close_price}")
        print(f"  Volume: {self.volume}")
