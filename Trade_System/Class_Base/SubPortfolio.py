# -*- coding: utf-8 -*-
##
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

from Trade_System.Class_Base.TradeRecord import *
from Trade_System.Class_Base.Loan import *
from Trade_System.Class_Base.OrderCost import *
from Trade_System.Class_Base.Slippage import *
from Trade_System.Class_Base.Position import *

import time
import datetime
from utils.date_handing import *  # 导入日期格式处理工具
##
__all__ = ["SubPortfolio"]


# 建立一个子账户的类立一个子账户的类，一个人可以拥有多个子账户,里面的操作是现实策略编写的原子操作
# 每一个原子操作都要对账户实现彻底的，实时的更新
class SubPortfolio:
    def __init__(self, mother_cash: float, master, type="stock", name="我的股票账户", Trading_rules="plus_one"):  # 股票和基金的保证金都为100%,默认最大仓位占比为100%
        self.master = master                  # master是它的父级，也就是Portfolio
        self.name = name                      # 设置账户名称
        self.type = type                      # 默认设置的账户类型为股票账户
        self.Trading_rules = Trading_rules    # 默认设置交易规则是T+1交易

        self.inout_cash = mother_cash         # 累积出入金,等于你总共投进去的钱
        self.available_cash = mother_cash     # 初始化资金等于初始入金
        self.transferable_cash = mother_cash  # 可取资金
        self.positions_value = 0.0            # 持仓目前的市场价值
        self.returns = 0.0                    # 计算当日相当于前日的收益率

        self.positions = {}                   # 用这个记录仓位信息，数量为负数的是做空，数量为正数的是做多，就这么简单
        self.loans = list()

        self.total_value = mother_cash         # 持仓价值加手里现金的价值
        self.total_liability = 0.0             # 总负债，发生融资行为时可能产生
        self.net_value = self.total_value - self.total_liability  # 净资产
        self.last_net_value = self.net_value   # 这个用于记录账户前一天的净资产

        self.cash_liability = 0.0              # 融资负债
        self.sec_liability = 0.0               # 融券负债

        self.create_time = time.time()  # 记录这个子账户创建的日期

        self.last_op = None                              # 记录上一次最近的操作

        self.trade_records = list()                      # 这个列表用于记录所有的交易记录
        self.trade_id = 0                                # 用于记录这是账户的第几笔操作
        self.order_cost = OrderCost(type)                # 这个是一个OrderCost对象，是跟手续费相关的业务
        self.slippage = PriceRelatedSlippage()           # 定义滑点
        self.volume_ratio = 1                            # 用于设置最大成交单位比例,相当于限制了单笔订单买入的仓位
        self.dt = datetime.datetime(2000, 1, 1)   # 这里先设置一下看看效果

    def get_position_by_code(self, code) -> Position:
        try:
            return self.positions[code]
        except:
            raise ValueError(f"该账户中没有发现标的{code}，获取仓位信息失败！")

    def add_position(self, code: str, quantity=0, price=0.0, buy_as_possible=False):
        price += self.slippage.get_slippage(price=price, type="buy")

        if buy_as_possible is True:
            quantity = (self.available_cash // price // 100) * 100

        self._is_add_position_properly(code=code, quantity=quantity, price=price)
        position = Position(code, self, quantity=quantity, price=price)
        self._add_position(code, position)   # 在这个层面上不对position内部进行操作，只添加标的的仓位
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def _is_add_position_properly(self, code, quantity=0, price=0.0):  # 用这个对输入的参数进行初步的检验
        # 使用这个函数判断添加仓位的参数是否符合规范
        if price <= 0:
            raise ValueError("输入的价格必须大于零！")
        if (not code.isdigit()) or (len(code) != 6):
            raise TypeError("输入的代码名称不符合规范，请输入六位，纯数字的字符串！")
        if (quantity % 100) != 0:
            raise ValueError(f"输入的交易数量{quantity}不是100的倍数，请重新输入！")
        if not self._is_enough_money(quantity, price, kind='buy'):
            raise TypeError("无法新增仓位了，已没有资金可以买入！")
        if self._is_more_than_max_position(code, quantity, price):
            raise TypeError("已经超过所设置的最大仓位了!")

    def _add_position(self, code, position):
        quantity = position.quantity
        price = position.average_cost
        if code not in self.positions:
            self.positions[code] = position  # 创建一个新的标的仓位
            self._update_account_info(quantity=quantity, price=price, kind='buy', code=code)
            self._add_a_trade_record(kind='buy', code=code, quantity=quantity, price=price)
        else:
            self._add_more_position(code, quantity, price)
            self._update_account_info(quantity=quantity, price=price, kind="buy_more", code=code)  # 更新子账户属性
            self._add_a_trade_record(kind='buy_more', code=code, quantity=quantity, price=price)

    def _add_more_position(self, code: str, quantity, price):  # 这个函数用于加仓
        position = self.positions[code]
        position.add_more_security(quantity, price)            # 在position层面进行操作

    def remove_position(self, code: str, price=0.0, quantity=0.0, sell_as_possible=False):
        # 卖出标的的总函数，回测时一般用context.dt做为date进行外部输入，用
        price += self.slippage.get_slippage(price=price, type="sell")
        if code not in self.positions:  # 持仓中没有要平仓的股票
            raise ValueError(f"No such position for code {code} found!")
        position = self.positions[code]  # 获取该代码的持仓信息
        if sell_as_possible is True:
            quantity = position.unlocked_sell_quantity  # 获取仓位中未锁定的股票数量，这是可以卖出的部分

        if position.quantity * quantity < 0:
            raise ValueError("卖出仓位数量的正负号出现错误！一定要与原有仓位同号")

        if abs(position.unlocked_sell_quantity) < abs(quantity):  # 发生报错，停止运行,这里要考虑做空的情况
            raise ValueError("可卖出的仓位数不足，无法进行卖出操作！")

        if abs(position.quantity) == abs(quantity) and (
                position.quantity == position.unlocked_sell_quantity):  # 卖出该标的的全部持仓
            self._remove_position(code, price)  # 这里要将原来的position占位删除
            print(f"已将代码为{code}的标的{quantity}股全部卖出")

        elif abs(position.unlocked_sell_quantity) == abs(quantity) and not (
                position.quantity == position.unlocked_sell_quantity):
            unlocked_sell_quantity = position.unlocked_sell_quantity
            self._partial_close_position(code, unlocked_sell_quantity, price)
            print("仓位中有部分仓位被锁定，只能部分卖出，已卖出" + str(unlocked_sell_quantity) + "股")
        else:
            self._partial_close_position(code, quantity, price)  # 卖出该标的的部分持仓
            print(f"已卖出{quantity}股，该仓位还剩{self.positions[code].quantity}股未卖出")
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def _remove_position(self, code: str, price: float):  # 将该标的的持仓全部卖出
        if code not in self.positions:
            raise TypeError("这个标的信息之前就不存在了")
        else:
            position = self.positions[code]
            quantity = position.quantity
            del self.positions[code]
            self._update_account_info(quantity=quantity, price=price, code=code, kind='sell_all')
            self._add_a_trade_record(kind="sell_all", code=code, quantity=quantity, price=price)

    def _partial_close_position(self, code: str, quantity: int, price: float):  # 卖出部分持仓
        position = self.positions[code]
        if abs(position.unlocked_sell_quantity) < abs(quantity):
            raise ValueError(f"Not enough quantity {self.positions[code].unlocked_sell_quantity} left for code {code}!")
        # 持仓标的不足再次报错
        position.partial_close_position(quantity, price)
        # 在仓位层面上进行操作
        self._update_account_info(quantity=quantity, price=price, code=code, kind='sell_partial')  # 在账户层面上进行更新
        self._add_a_trade_record(kind='sell_partial', code=code, quantity=quantity, price=price)

    # 用于更新账户的信息
    def _update_account_info(self, kind='buy', quantity=0, price=0.0, code=None, loan=None, long=True):
        if kind == 'buy':
            self.available_cash -= quantity * price + self._calculate_fee(quantity, price, long, kind=kind)
            self.transferable_cash -= quantity * price + self._calculate_fee(quantity, price, long,kind=kind)
            # 买入股票即被自动视为冻结
            if self.transferable_cash <= 0:
                self.transferable_cash = 0  # 可取资金最小为0
            self._positions_statics()
            self.last_op = "新增仓位：" + code + '   ' + str(quantity)
        elif kind == 'buy_more':
            self.available_cash -= quantity * price + self._calculate_fee(quantity, price, True, kind=kind)
            self.transferable_cash -= quantity * price + self._calculate_fee(quantity, price, True, kind=kind)
            if self.transferable_cash <= 0:
                self.transferable_cash = 0  # 可取资金最小为0
            self._positions_statics()
            self.last_op = '增加仓位：' + code + '   ' + str(quantity)
        elif kind == "sell_all":
            self.available_cash += quantity * price - self._calculate_fee(quantity, price, True, kind=kind)
            self._positions_statics()  # 重新统计仓位信息，并进行更新
            self.last_op = '清除仓位：' + code + '   ' + str(quantity)
        elif kind == "sell_partial":
            self.available_cash += quantity * price - self._calculate_fee(quantity, price, True, kind=kind)
            self._positions_statics()  # 重新统计仓位信息并进行更新
            self.last_op = '减少仓位：' + code + '   ' + str(quantity)
        elif kind == "loan_cash":
            self.loans.append(loan)
            self.available_cash += loan.principal
            self.transferable_cash += loan.principal
            self.cash_liability += loan.principal
            self.total_liability = self.cash_liability + self.sec_liability
            self.total_value = self.total_liability + self.net_value
            self.last_op = "融资：" + str(loan.principal) + '   ' + "利率：" + str(loan.rate)
        elif kind == "loan_sec":
            self.loans.append(loan)
            self.available_cash += loan.principal
            self.transferable_cash += loan.principal
            self.cash_liability += loan.principal
            self.total_liability = self.cash_liability + self.sec_liability
            self.total_value = self.total_liability + self.net_value
            self.last_op = "融券：" + str(loan.principal) + '   ' + "利率：" + str(loan.rate)
        else:
            raise ValueError("参数输入错误,没有这种操作类型")

    def update_date_info(self, date):       # 用这个函数更新账户的日期信息，每个交易日开头会调用一次
        self.dt = long_datestr_to_dd(date)  # 直接传入 date
        self.last_net_value = self.net_value
        self.returns = 0                    # 重新归零等待后续的计算
        self.transferable_cash = self.available_cash
        for position in self.positions.values():
            position.update_date_info(date=date)

    def update_price_info(self):            # 用这个函数在每个交易日收盘时调用一次，对一天的收益率进行统计
        for position in self.positions.values():
            position.update_for_current_price()
        self._positions_statics()
        self.returns = (self.net_value - self.last_net_value) / self.last_net_value
        self.master.update_Portfolio_info()

    def _positions_statics(self):
        self.positions_value = 0    # 下面进行重新统计仓位市值
        for position in self.positions.values():
            self.positions_value += position.market_value
        self.total_value = self.available_cash + self.positions_value
        self.net_value = self.total_value - self.total_liability

    def _add_a_trade_record(self, kind: str, code: str, quantity: int, price: float):
        self.trade_id += 1
        trade_record = TradeRecord(self.trade_id, kind, code, quantity, price, self.dt)
        self.trade_records.append(trade_record)  # 添加一条交易记录


    def deposit(self, amount: float):  # 给账户充值
        # 需要加一个判定
        if self.master.remaining_recharge < amount:
            raise ValueError(f"已超出可以充值的限额，充值失败!目前可充值余额：{self.master.remaining_recharge}")
        else:
            self.inout_cash += amount
            self.available_cash += amount
            self.transferable_cash += amount
            self.net_value += amount
            self.total_value = self.net_value + self.total_liability
            self.master.remaining_recharge -= amount
            self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def withdraw(self, amount: float):  # 用于从账户中提取现金
        # 需要加一个判定
        if self.transferable_cash < amount:
            raise ValueError(f"已超出可以取钱的限额，取钱失败!目前可取钱的金额为：{self.transferable_cash}")
        else:
            self.inout_cash -= amount
            self.available_cash -= amount
            self.transferable_cash -= amount
            self.net_value -= amount
            self.total_value = self.net_value + self.total_liability
            self.master.remaining_recharge += amount
            self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def using_loan(self, principal, rate, term, load_type="cash"):  # 这个函数用来使用负债,又可以分为融资负债和融券负债两种，也就是所谓的上杠杆
        L = Loan(principal, rate, term, load_type)
        self._update_account_info(kind="loan_" + load_type, loan=L)
        self.master.update_Portfolio_info()  # 对外部的大账户进行手动更新

    def _calculate_fee(self, quantity: int, price: float, long=True, kind='buy') -> float:  # 这个函数用来计算这个账户所需要的手续费
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

    def _is_enough_money(self, quantity, price, kind, long=True):  # 这个函数专门用于判断钱是否购买股票
        order_value = abs(quantity) * price + self._calculate_fee(price, abs(quantity), long, kind=kind)
        if self.available_cash >= order_value:
            return True, None
        else:
            miss_cash = order_value - self.available_cash  # 计算缺失的现金
            return False, miss_cash

    def _is_more_than_max_position(self, code: str, quantity, price) -> bool:  # 用这个函数判断是否超过最大仓位了
        try:
            position = self.positions[code]
            market_value_after_add = position.market_value + quantity * price
        except:
            market_value_after_add = quantity * price
        if market_value_after_add <= self.volume_ratio * self.total_value:
            return False
        else:
            return True

    def __repr__(self):  # 用于定义显示的
        """返回 SubPortfolio 对象的字符串表示形式"""
        return f"SubPortfolio(inout_cash={self.inout_cash}, available_cash='{self.available_cash}', transferable_cash='{self.transferable_cash}', total_value={self.total_value}, total_liability={self.total_liability}, net_value={self.net_value}, return={self.returns}, create_time={self.create_time}, dt={self.dt}, last_net_value={self.last_net_value} )"


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
    Sp.add_position('601127', 300, 30)
    Sp.add_position('600436', 200, 10)
    Sp.add_position('601127', 100, 32)
    Sp.remove_position("601127", 20)
    Sp.remove_position("601127", 20)
    Sp.add_position('600436', 200, 10)
    print(Sp)
    print(Sp.loans[0])
    print(Sp.loans[1])
    # SP=SubPortfolio()

# 测试买入操作
# %%
