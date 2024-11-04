# -*- coding: utf-8 -*-
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

import time
import akshare as ak
from utils.date_handing import *  # 导入日期格式处理工具

# %%
__all__ = ["Position"]


# %% 定义一个Position类用于存储单个标的的仓位信息，一般用户不会在这个层面上进行调用方法，最底层是SubPortfolio的原子方法
# 注意，一般股票做空很难，而期货可以做空且是T+0交易，不用考虑锁定的交易。
class Position:
    def __init__(self, code: str, master, quantity=0, price=0.0):  # 这个master是SubPortfolio对象
        # 默认开始没有进行任何交易，交易产生的变换都是之后下单产生的

        self.master = master        # 所属的子账户对象
        self.code = code            # 标的代码

        self.quantity = quantity    # 标的数量
        self.average_cost = price   # 标的的平均成本

        self.market_value = quantity * price                                 # 在做空时，市场价值为负数
        self.tied_up_capital = self.market_value                             # 标的的占用资金，包括仓位和下单占用资金
        self.position_profit = 0                                             # 用这个来记录仓位盈亏的金额

        self.create_time = time.time()                                       # 标的仓位创建时间
        self.dt = self.master.dt


        if master.Trading_rules != "plus_zero":                          # 如果不是T+0交易制度
            self.unlocked_sell_quantity = 0                                  # 锁定这一天买的所有股票，不能卖出
        else:
            self.unlocked_sell_quantity = quantity                           # 在任何时候都不进行锁定，可以任意卖出

    def partial_close_position(self, quantity, price):  # 相当于减仓操作，能做空的时候意味着做空
        if self.master.Trading_rules != "plus_zero":   # 这时候说明不能做空且是T+1的
            if abs(self.unlocked_sell_quantity) < abs(quantity):
                raise TypeError("输入的参数值已经超出了最大的可卖出单位数")
            self.quantity -= quantity
            self.unlocked_sell_quantity -= quantity

            self.tied_up_capital -= self.quantity * price
            self.average_cost = (self.average_cost * (quantity + self.quantity) - price * quantity) / self.quantity
            self.market_value = price * self.quantity
            self.position_profit = -self.average_cost * self.quantity + self.market_value
        else:  # 这时候说明能做空且是T+0的
            self._non_direction_trading(quantity=quantity, price=price)
            pass

    def add_more_security(self, quantity, price):  # 这个函数用于加仓
        if self.master.Trading_rules != "plus_zero":
            if price <= 0 or (quantity < 0):
                raise TypeError("加仓参数输入错误")
            self.quantity += quantity

            self.average_cost = (quantity * price + self.average_cost * (self.quantity - quantity)) / self.quantity
            self.market_value = self.quantity * price
            self.tied_up_capital += self.quantity * price
        else:   # 这时候说明能做空且是T+0的
            self._non_direction_trading(quantity=quantity, price=price)
            pass

    def _non_direction_trading(self, quantity, price):
        self.quantity += quantity
        self.unlocked_sell_quantity += quantity

        self.tied_up_capital = self.quantity * price + 0   # 借出股票会增加账户中的现金,所以锁定的现金减少
        self.average_cost = (self.average_cost * (self.quantity-quantity) + price * quantity) / self.quantity
        self.market_value = price * self.quantity          # 借出股票对你未来的收益预期是负的
        self.position_profit = -self.average_cost * abs(self.quantity) + self.market_value

    def update_date_info(self, date):
        # 用这个函数更新账户的日期信息
        self.dt = long_datestr_to_dd(str(date))
        self.unlocked_sell_quantity = self.quantity  # 直接全部解锁

    def update_for_current_price(self):  # 用这个函数在每一天操作后获得当天的收盘价，对仓位的各种价值进行更新，这个后面处理，因为获取收益曲线需要这个东西
        day_str = dd_to_short_datestr(self.dt)
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.code, period="daily", start_date=day_str,
                                                end_date=day_str, adjust="hfq")  # 整个系统均建立在后赋权的基础上
        close_price = float(stock_zh_a_hist_df["收盘"].iloc[0])
        self.market_value = self.quantity * close_price        # 在做空时，quantity一般为负数
        self.tied_up_capital = self.quantity * close_price     # 标的的占用资金，包括仓位和下单占用资金
        self.position_profit = -self.average_cost * abs(self.quantity) + self.market_value  # 用这个来记录仓位盈亏的金额

    @property
    def value(self):  # 输出现有持仓外加挂单的总价值
        return self.market_value + sum([order.value for type in self.open_orders for order in self.open_orders[type]])

    def __repr__(self):
        return f"Position(code='{self.code}', quantity={self.quantity}, average_cost={self.average_cost}, market_value={self.market_value})"
