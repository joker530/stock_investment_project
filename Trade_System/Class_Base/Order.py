# -*- coding: utf-8 -*-
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

from enum import Enum
from Trade_System.Class_Base.Position import *  # 导入外围类
from Trade_System.Class_Base.SubPortfolio import *
from Trade_System.Class_Base.Portfolio import *
import time

# %%  导出这些类
__all__ = ["OrderStyle", "MarketOrderStyle", "Order", "OrderStatus"]


# %% 定义一个类用于表示下单的类型，输入订单的数量，订单的类型，挂单的价格和止损单的触发价格
class OrderStyle:
    def __init__(self, amount: float, style: str, limit_price: float = None, stop_price: float = None,
                 trailing_percent: float = None):
        self.amount = amount  # 订单数量
        self.style = style  # 订单类型，一般为'limit'和'market'两种，也就是限价单和市价单
        self.limit_price = limit_price  # 限价单价格
        self.stop_price = stop_price  # 止损单触发价格，下单成交后需要时可以即使追踪

    def __repr__(self):
        """返回 OrderStyle 对象的字符串表示形式"""
        return (f"OrderStyle(amount={self.amount}, style='{self.style}', limit_price={self.limit_price}, "
                f"stop_price={self.stop_price})")


# %% 市价单的类
class MarketOrderStyle(OrderStyle):
    def __init__(self, current_price, limit_price=None):
        super().__init__(limit_price=limit_price, style='market')  # 调用父类的预定义的方法
        self.current_price = current_price

    def __repr__(self):
        """返回 MarketOrderStyle 对象的字符串表示形式"""
        return f"MarketOrderStyle(amount={self.amount})"


# %% 订单状态，用于显示成没成交等情况，这里罗列了所有的情况
class OrderStatus(Enum):
    # 订单新创建未委托，用于盘前/隔夜单，订单在开盘时变为 open 状态开始撮合
    new = 8

    # 订单未完成, 无任何成交
    open = 0

    # 订单未完成, 部分成交
    filled = 1

    # 订单完成, 已撤销, 可能有成交, 需要看 Order.filled 字段
    canceled = 2

    # 订单完成, 交易所已拒绝, 可能有成交, 需要看 Order.filled 字段
    rejected = 3

    # 订单完成, 全部成交, Order.filled 等于 Order.amount
    held = 4

    # 订单取消中，只有实盘会出现，回测/模拟不会出现这个状态
    pending_cancel = 9
# %% 下单类Order,用于记录下单的操作，通常在回测环境中没有撮合系统，所以也没有订单


class Order:
    def __init__(self, code: str, order_type: str, price: float, quantity: int, long: bool, outer: Position,
                 status=OrderStatus.open):
        self.order_type = order_type
        if self.order_type == "limit":  # 如果是限价单
            self.OrderStyle = OrderStyle(quantity, self.order_type)
        elif self.order_type == "market":  # 如果是市价单
            self.OrderStyle = MarketOrderStyle(current_price=price)
        else:
            raise TypeError("订单的类型输入错误")
        self.code = code
        self.price = price
        self.quantity = quantity
        self.already_cost = 0  # 这里表示的是订单已经成交的数额
        self.long = long
        self.outer = outer  # 定义外围类，订单的外围类是仓位，在Position层面可以控制下单对象的产生与销毁
        self.status = status  # 这里输入的是像OrderStatus.open，这种，描述的是订单此时的状态
        self.create_time = time.time()  # 记录创建的时间戳

    def cancel(self, quantity: int):  # 撤销部分订单，如果全部撤销需要改变订单的状态
        def change_Order(self, quantity):  # 用于更新订单类
            if quantity > self.quantity:
                self._update_Order_Info(-self.quantity, -self.price)  # 清空这两个参数
                self.status = OrderStatus.canceled  # 设置订单状态为取消
            else:
                self._update_Order_Info(-quantity, 0)  # 这个操作相当于卖出部分仓位
        # def change_Position(self):  #用于更新上一级的仓位类

    def deal_part(self, quantity: int):  # 这个方法在订单发生了成交时进行调用,模拟成交时发生的过程
        if quantity < 0:
            raise ValueError("成交的数量不能为负数")
        if quantity >= self.quantity:
            self.already_cost += (self.quantity) * (self.price)
            self._update_Order_Info(-self.quantity, -self.price)
            self.status = OrderStatus.held  # 订单完成，全部成交
        else:
            self.already_cost += quantity * self.price
            self._update_Order_Info(-quantity, 0)
            self.status = OrderStatus.filled  # 订单未完成，部分成交

    def _update_Order_Info(self, quantiy_delta, price_delta):
        self.quantity += quantiy_delta
        self.price += price_delta

    @property  # 这是一个装饰器，这样不用输入参数就能显示对象的总价值了
    def value(self):
        return self.price * self.quantity


##

if __name__ == "__main__":
    p1 = Portfolio(mother_cash=100000)
    s1 = SubPortfolio(inout_cash=10000, master=p1)
    position = Position(code='601127', master=s1)
    order1 = Order('601127', 'limit', 30.0, 500, True, position)
    order1.cancel(300)
    order1.deal_part(100)
    order1.deal_part(100)
    print(order1.quantity)
    print(order1.status)
    print(order1.price)
    