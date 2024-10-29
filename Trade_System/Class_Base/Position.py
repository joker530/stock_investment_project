# -*- coding: utf-8 -*-
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

import time
import akshare as ak

# %%
__all__ = ["Position"]


# %% 定义一个Position类用于存储单个标的的仓位信息
class Position:
    def __init__(self, code: str, master, long=True, quantity=0, price=0.0,  # 这个master是
                 Trading_rules="plus_one"):  # 默认开始没有进行任何交易，交易产生的变换都是之后下单产生的
        self.master = master  # 所属的子账户对象
        self.code = code  # 标的代码
        self.quantity = quantity  # 标的数量
        self.average_cost = price  # 标的的平均成本
        self.long = long  # long属性用来区分多空方向
        self.market_value = quantity * price if long else -quantity * price  # 在做空时，quantity一般为负数
        self.tied_up_capital = self.market_value   # 标的的占用资金，包括仓位和下单占用资金
        self.create_time = time.time()
        self.date = self.master.master.current_trade_date  # 表示此时回测的日期
        if Trading_rules != "plus_zero":
            self.unlocked_sell_quantity = 0  # 锁定这一天买的所有股票，不能卖出
        else:
            self.unlocked_sell_quantity = quantity  # 在任何时候都不进行锁定，可以任意卖出

    def partial_close_position(self, quantity, price):  # 相当于减仓操作
        if abs(self.unlocked_sell_quantity) < abs(quantity):
            raise TypeError("输入的参数值已经超出了最大的可卖出单位数")
        self.quantity -= quantity
        self.unlocked_sell_quantity -= quantity

        self.tied_up_capital = (self.quantity) * price + 0
        self.average_cost = (self.average_cost * (quantity + self.quantity) - price * quantity) / self.quantity
        self.market_value = price * self.quantity

    def close_whole_position(self, quantity, price, long):  # 这个函数暂时不用
        if abs(self.unlocked_sell_quantity) <= abs(quantity):
            raise TypeError("T+n交易制度，无法全部卖出!")

    def update_position_day(self, date):  # 在子账户层面，每进行一个操作就更新一次
        if self.date != date:
            self.unlocked_sell_quantity = self.quantity
            self.date = date

    def add_more_security(self, quantity, price, long):  # 这个函数用于加仓
        if price <= 0 or (quantity < 0 and long) or (quantity > 0 and not long):
            raise TypeError("加仓参数输入错误")
        self.average_cost = (abs(quantity) * price + self.tied_up_capital) / (self.quantity + quantity)
        self.market_value = (self.quantity + quantity) * price
        self.quantity += quantity

    def close(self, quantity: int, price: float):  # 以一定的数量和价格进行平仓
        if quantity > self.quantity:  # 没有足够的仓位进行这个数量的平仓
            raise ValueError("Not enough quantity to close position!")
        if self.long:
            pnl = quantity * (price - self.average_cost)  # 多头平仓
        else:
            pnl = quantity * (self.average_cost - price)  # 空头平仓
        self.quantity -= quantity  # 降低持仓的标的数量
        self.market_value = self.quantity * self.average_cost if self.long else -self.quantity * self.average_cost

    def update_for_current_price(self):  # 用这个函数在每一天操作后获得当天的收盘价，对仓位的各种价值进行更新
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.code, period="daily", start_date="20240528",
                                                end_date='20240528', adjust="hfq")  # 整个系统均建立在后赋权的基础上
        pass

    @property
    def value(self):  # 输出现有持仓外加挂单的总价值
        return self.market_value + sum([order.value for type in self.open_orders for order in self.open_orders[type]])

    def __repr__(self):
        return f"Position(code='{self.code}', long={self.long}, quantity={self.quantity}, average_cost={self.average_cost}, market_value={self.market_value})"
