# -*- coding: utf-8 -*-
##
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

from Trade_System.Class_Base.Position import *
from Trade_System.Class_Base.TradeRecord import *
from Trade_System.Class_Base.Loan import *
from Trade_System.Class_Base.OrderCost import *
from Trade_System.Class_Base.Slippage import *
from datetime import datetime
import time
import datetime

##
__all__ = ["SubPortfolio"]


# %% 建立一个子账户的类立一个子账户的类，一个人可以拥有多个子账户
class SubPortfolio:
    def __init__(self, inout_cash: float, master, margin=1, type="stock", name="我的股票账户",
                 max_size_rate=1):  # 股票和基金的保证金都为100%,默认最大仓位占比为100%
        self.master = master  # master是它的父级，也就是Portfolio
        self.inout_cash = inout_cash  # 累积出入金,等于你总共投进去的钱
        self.available_cash = inout_cash  # 初始化资金等于初始入金
        self.transferable_cash = inout_cash  # 可取资金
        self.locked_cash = 0.0  # 挂单锁住资金
        self.margin = margin
        self.positions = {}
        self.long_positions = {}
        self.short_positions = {}
        self.total_value = inout_cash  # 持仓价值加手里现金的价值
        self.total_liability = 0  # 总负债，发生融资行为时可能产生
        self.net_value = inout_cash  # 净资产
        self.cash_liability = 0  # 融资负债
        self.sec_liability = 0  # 融券负债
        self.interest = 0.06  # 假设每年融资的钱的利息为6%
        self.returns = 0.0  # 计算当日相当于前日的收益率
        self.positions_value = 0.0  # 持仓目前的市场价值
        self.type = type  # 默认设置的账户类型为股票账户
        self.last_op = None  # 记录最近的操作
        self.create_time = time.time()  # 记录这个子账户创建的日期
        self.last_op_date = datetime.date(1990, 1, 1)  # 这个用于记录最后操作的日期
        self.date = self.last_op_date
        self.last_total_value = self.total_value  # 这个用于记录账户前一天的总市值
        self.trade_records = list()  # 这个列表用于记录所有的交易记录
        self.trade_id = 0
        self.name = name
        self.last_profit_rate = 0
        self.loans = list()
        self.max_size_rate = max_size_rate
        self.order_cost = OrderCost(type)  # 这个是一个OrderCost对象，是跟手续费相关的业务
        self.slippage = PriceRelatedSlippage()  # 定义滑点
        self.volume_ratio = 1

    def _remove_position(self, code: str, price: float, long=True):  # 将该标的的持仓全部卖出
        if code not in self.positions:
            raise TypeError("这个标的信息之前就不存在了")
        else:
            position = self.positions[code]
            quantity = position.quantity
            del self.positions[code]
            if position.long:
                del self.long_positions[code]  # 删除多头持仓
            else:
                del self.short_positions[code]  # 删除空头持仓
            self._update_account_info(quantity=quantity, price=price, code=code, kind='sell_all')
            self._add_a_trade_record(kind="sell_all", code=code, quantity=quantity, price=price)

    # 卖出标的的总函数，回测时一般用context.dt做为date进行外部输入，用
    def remove_position(self, code: str, long: bool, price: float, quantity=None):
        self._update_account_date()  # 先根据操作日期更新账户
        price += self.slippage.get_slippage(price=price, type="sell")
        if code not in self.positions:  # 持仓中没有要平仓的股票
            raise ValueError(f"No such position for code {code} found!")

        position = self.positions[code]  # 获取该代码的持仓信息
        if quantity == None:
            quantity = position.unlocked_sell_quantity  # 获取仓位中未锁定的股票数量，这是可以卖出的部分

        if position.quantity * quantity < 0:
            raise ValueError("卖出仓位数量的正负号出现错误！一定要与原有仓位同号")

        if abs(position.unlocked_sell_quantity) < abs(quantity):  # 发生报错，停止运行,这里要考虑做空的情况
            raise ValueError("可卖出的仓位数不足，无法进行卖出操作！")

        if abs(position.quantity) == abs(quantity) and (
                position.quantity == position.unlocked_sell_quantity):  # 卖出该标的的全部持仓
            self._remove_position(code, price, long)  # 这里要将原来的position占位删除
            print("已将代码为{}的标的全部卖出".format(code))

        elif abs(position.unlocked_sell_quantity) == abs(quantity) and not (
                position.quantity == position.unlocked_sell_quantity):
            unlocked_sell_quantity = position.unlocked_sell_quantity
            self._partial_close_position(code, quantity, price, long)
            print("仓位中有部分仓位被锁定，只能部分卖出，已卖出" + str(abs(quantity)))
        else:
            self._partial_close_position(code, quantity, price, long)  # 卖出该标的的部分持仓
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def _partial_close_position(self, code: str, quantity: int, price: float, long: bool):  # 卖出部分持仓
        position = self.positions[code]
        if position.long and not long or not position.long and long:  # 如果做多做空方向不同则报错
            raise ValueError(f"Cannot partial close a position with different long/short direction!")
        if abs(position.quantity) < abs(quantity):
            raise ValueError(f"Not enough quantity {self.positions[code].quantity} left for code {code}!")  # 持仓标的不足再次报错
        position.partial_close_position(quantity, price)  # 在仓位层面上进行操作
        self._update_account_info(quantity=quantity, price=price, code=code, kind='sell_partial')  # 在账户层面上进行更新
        self._add_a_trade_record(kind='sell_partial', code=code, quantity=quantity, price=price)

    # 用于更新账户的信息
    def _update_account_info(self, kind='buy', quantity=0, price=0, code=None, loan=None, long="True"):
        if kind == 'buy':
            self.available_cash -= abs(quantity) * price + self.calculate_fee(quantity, price, long, kind=kind)
            self.transferable_cash -= abs(quantity) * price + self.calculate_fee(quantity, price, long,
                                                                                 kind=kind)  # 买入股票即被自动视为冻结
            if self.transferable_cash <= 0:
                self.transferable_cash = 0  # 可取资金最小为0
            self._positions_statics()
            self.returns = self.get_current_profit_rate()
            self.last_op = "新增仓位：" + code + '   ' + str(quantity)
        elif kind == 'buy_more':
            self.available_cash -= abs(quantity) * price + self.calculate_fee(quantity, price, True, kind=kind)
            self.transferable_cash -= abs(quantity) * price + self.calculate_fee(quantity, price, True, kind=kind)
            if self.transferable_cash <= 0:
                self.transferable_cash = 0  # 可取资金最小为0
            self._positions_statics()
            self.returns = self.get_current_profit_rate()
            self.last_op = '增加仓位：' + code + '   ' + str(quantity)
        elif kind == "sell_all":
            self.available_cash += abs(quantity) * price - self.calculate_fee(quantity, price, True, kind=kind)
            self._positions_statics()  # 重新统计仓位信息，并进行更新
            self.returns = self.get_current_profit_rate()
            self.last_op = '清除仓位：' + code + '   ' + str(quantity)
        elif kind == "sell_partial":
            self.available_cash += abs(quantity) * price - self.calculate_fee(quantity, price, True, kind=kind)
            self._positions_statics()  # 重新统计仓位信息并进行更新
            self.returns = self.get_current_profit_rate()
            self.last_op = '减少仓位：' + code + '   ' + str(quantity)
        elif kind == "loan_cash":
            self.loans.append(loan)
            self.available_cash += loan.principal
            self.transferable_cash += loan.principal
            self.cash_liability += loan.principal
            self.total_liability = self.cash_liability + self.sec_liability
            self.total_value = self.total_liability + self.net_value
            self.last_op = "融资：" + str(loan.principal) + '   ' + "利率：" + str(loan.rate)
            self.last_total_value += loan.principal
        elif kind == "loan_sec":
            self.loans.append(loan)
            self.available_cash += loan.principal
            self.transferable_cash += loan.principal
            self.cash_liability += loan.principal
            self.total_liability = self.cash_liability + self.sec_liability
            self.total_value = self.total_liability + self.net_value
            self.last_op = "融券：" + str(loan.principal) + '   ' + "利率：" + str(loan.rate)
            self.last_total_value += loan.principal
        else:
            raise ValueError("参数输入错误,没有这种操作类型")

    def _restart_value(self):  # 把那些要统计仓位的变量都归零
        self.positions_value = 0

    def _positions_statics(self):
        self._restart_value()
        values = list(self.positions.values())
        for i in range(len(values)):
            self.positions_value += values[i].market_value
        self.total_value = self.available_cash + self.positions_value
        self.net_value = self.total_value - self.total_liability

    def add_position(self, code: str, long: bool, quantity=0, price=0.0):
        if not self._is_enough_money(quantity, price, kind='buy'):
            raise TypeError("无法新增仓位了，已没有资金可以买入！")
        if self._is_more_than_max_position(code, quantity, price):
            raise TypeError("已经超过所设置的最大仓位了!")
        price += self.slippage.get_slippage(price=price, type="buy")
        position = Position(code, self, long=long, quantity=quantity, price=price)
        self._update_account_date()  # 在操作前先对日期进行更新
        self._add_position(code, position, long)  # 在这个层面上不对position内部进行操作，只添加标的的仓位
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def _add_more_position(self, code: str, quantity, price):  # 这个函数用于加仓
        position = self.positions[code]
        position.add_more_security(quantity, price, position.long)  # 在position层面进行操作

    def _add_position(self, code, position: Position, long=True):
        quantity = position.quantity
        price = position.average_cost
        if code not in self.positions:
            self.positions[code] = position  # 创建一个新的标的仓位
            if long:
                self.long_positions[code] = position  # 两个字典的对象始终保持一致
            else:
                self.short_positions[code] = position
            self._update_account_info(quantity=quantity, price=price, kind='buy', code=code)
            self._add_a_trade_record(kind='buy', code=code, quantity=quantity, price=price)
        else:
            self._add_more_position(code, quantity, price)
            self._update_account_info(quantity=quantity, price=price, kind="buy_more", code=code)  # 更新子账户属性
            self._add_a_trade_record(kind='buy_more', code=code, quantity=quantity, price=price)

    def get_current_profit_rate(self):
        return (self.total_value - self.last_total_value) / self.last_total_value

    def _update_account_date(self):  # 这里的date形式是年-月-日的形式,
        if self.date > self.master.current_trade_date:
            raise TypeError("你当前输入的日期没有与原日期方向保持一致！")
        if self.date != self.master.current_trade_date:
            self.last_profit_rate = (self.total_value - self.last_total_value) / self.last_total_value
            self.last_total_value = self.total_value
            self.transferable_cash = self.available_cash
            self.date = self.master.current_trade_date  # 更新日期
            self.last_op_date = self.master.current_trade_date
            for position in self.positions.values():  # 把所有的仓位对象进行更新
                position.update_position_day(self.master.current_trade_date)

    def _add_a_trade_record(self, kind: str, code: str, quantity: int, price: float):
        self.trade_id += 1
        trade_record = TradeRecord(self.trade_id, kind, code, quantity, price, self.date)
        self.trade_records.append(trade_record)  # 添加一条交易记录

    def _is_enough_money(self, quantity, price, kind, long="True"):  # 这个函数专门用于判断钱是否购买股票
        order_value = abs(quantity) * price + self.calculate_fee(price, abs(quantity), long, kind=kind)
        if self.available_cash >= order_value:
            return True, None
        else:
            miss_cash = order_value - self.available_cash  # 计算缺失的现金
            return True, miss_cash

    def _is_more_than_max_position(self, code: str, quantity, price):  # 用这个函数判断是否超过最大仓位了
        try:
            position = self.positions[code]
            market_value_after_add = position.market_value + abs(quantity) * price
        except:
            market_value_after_add = abs(quantity) * price
        if market_value_after_add <= self.max_size_rate * self.total_value:
            return False
        else:
            return True

    def update_market_value(self, code: str, price: float):  # 更新账户的总市值
        if code not in self.positions:
            raise ValueError(f"No such position for code {code} found!")
        for position in self.positions[code]:
            position.update_market_value(price)
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def deposit(self, amount: float):  # 给账户充值
        self.inout_cash += amount
        self.available_cash += amount
        self.transferable_cash += amount
        self.net_value += amount
        self.total_value = self.net_value + self.total_liability
        self.master.mother_cash += amount
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def withdraw(self, amount: float):  # 用于从账户中提取现金
        if self.transferable_cash < amount:
            raise ValueError("Not enough available cash to withdraw!")
        self.inout_cash -= amount
        self.available_cash -= amount
        self.transferable_cash -= amount
        self.net_value -= amount
        self.total_value = self.net_value + self.total_liability
        self.master.mother_cash -= amount
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def calculate_fee(self, quantity: int, price: float, long=True, kind='buy'):  # 这个函数用来计算这个账户所需要的手续费
        if long and not (kind not in ["buy", "buy_more"]):  # 如果即时做多且买入或买入更多仓位
            order_value = abs(quantity) * price
            commission = self.order_cost.buy_fee(order_value)  # 假设手续费为最大值 5 元或按成交金额的 0.025%
        elif long and not (kind not in ["sell_all", "sell_partial"]):
            order_value = abs(quantity) * price
            commission = self.order_cost.sell_fee(order_value)  # 假设空头手续费稍高，为最大值 5 元或按成交金额的 0.05%
        elif not long and not (kind not in ["buy", "buy_more"]):
            order_value = abs(quantity) * price
            commission = self.order_cost.buy_fee(order_value)
        elif not long and not (kind not in ["sell_all", "sell_partial"]):
            order_value = abs(quantity) * price
            commission = self.order_cost.sell_fee(order_value)
        else:
            raise TypeError("没有这种计算费用的方式！")
        return commission

    def using_loan(self, principal, rate, term, load_type="cash"):  # 这个函数用来使用负债,又可以分为融资负债和融券负债两种，也就是所谓的上杠杆
        L = Loan(principal, rate, term, load_type)
        self._update_account_info(kind="loan_" + load_type, loan=L)
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def __repr__(self):  # 用于定义显示的
        """返回 SubPortfolio 对象的字符串表示形式"""
        return f"SubPortfolio(inout_cash={self.inout_cash}, available_cash='{self.available_cash}', transferable_cash='{self.transferable_cash}', total_value={self.total_value}, total_liability={self.total_liability}, net_value={self.net_value}, returns={self.returns}, create_time={self.create_time}, last_op_date={self.last_op_date}, date={self.date}, last_profit_rate={self.last_profit_rate}, last_total_value={self.last_total_value} )"


'''
在Python中，可变对象包括列表（list）、字典（dict）、集合（set）和用户自定义的类实例等类型。
这些对象当你通过其中一个变量修改对象时，另一个变量也会受到影响。
'''
# %% 测试检验
if __name__ == "__main__":
    from Trade_System.Class_Base.Portfolio import *

    P = Portfolio(200000)
    Sp = SubPortfolio(100000, master=P)
    Sp.using_loan(100000, 0.06, 1.5)  # 这里的期限的单位是年
    Sp.using_loan(100000, 0.1, 0.6, load_type="sec")
    date1 = datetime.date(2023, 5, 4)
    date2 = datetime.date(2023, 5, 6)
    date3 = datetime.date(2023, 5, 6)
    date4 = datetime.date(2023, 5, 7)
    Sp.add_position('601127', True, 300, 30)
    Sp.add_position('600436', True, 200, 10)
    Sp.add_position('601127', True, 100, 32)
    Sp.remove_position("601127", True, 20)
    Sp.remove_position("601127", True, 20)
    Sp.add_position('600436', True, 200, 10)
    print(Sp)
    print(Sp.loans[0])
    print(Sp.loans[1])
    # SP=SubPortfolio()

# 测试买入操作
# %%
