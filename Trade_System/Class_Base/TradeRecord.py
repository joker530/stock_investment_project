# -*- coding: utf-8 -*-
"""
Created on Fri May  5 20:29:43 2023

@author: Administrator
"""
# 这个类专门用于记录一条回测交易记录
# %%
__all__ = ["TradeRecord"]

import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)


# %%
class TradeRecord:
    def __init__(self, trade_id, trade_op, code: str, quantity, price: float, date):
        self.trade_id = trade_id
        self.trade_op = trade_op
        self.code = code
        self.quantity = quantity
        self.price = price
        self.date = date

    def __repr__(self):
        return f"Trade ID: {self.trade_id}, Operation: {self.trade_op}, Code: {self.code}, Quantity: {self.quantity}, Price: {self.price}, Date: {self.date}"
