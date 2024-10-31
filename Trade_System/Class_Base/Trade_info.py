# -*- coding: utf-8 -*-
__all__ = ["Trade", "TradeList"]

import datetime
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)


# %% 订单的交易记录，用于记录每一条交易的信息，注意是已经成交的
class Trade:
    def __init__(self, order_id: int, trade_time, code: str, price: float, amount: int, long=True):
        self.order_id = order_id  # 记录Trade记录的id号
        self.trade_time = trade_time
        self.code = code
        self.price = price
        self.amount = amount
        self.long = long

    def __repr__(self):  # 用于定义显示的
        """返回 Trade 对象的字符串表示形式"""
        return f"Trade(order_id={self.order_id}, trade_time='{self.trade_time}', code='{self.code}', price={self.price}, amount={self.amount}, long={self.long})"


# %% 订单的列表
class TradeList:
    def __init__(self):
        self.trades = []

    def add_trade(self, trade: Trade) -> None:  # ->None表示这个方法没有返回值
        """添加一条 Trade 记录"""
        self.trades.append(trade)

    def remove_trade(self, trade: Trade) -> None:
        """移除一条 Trade 记录"""
        self.trades.remove(trade)

    def get_trades(self) -> list:  # 这个方法返回一个列表的数据类型
        """获取所有 Trade 记录"""
        return self.trades

    def get_trade_by_id(self, order_id: int):
        """根据 ID 号获取指定的 Trade 记录"""
        for trade in self.trades:
            if trade.order_id == order_id:
                return trade
        return None


# %%
if __name__ == "__main__":
    t = Trade(1, datetime.datetime.now(), '601127', 30, 300)
