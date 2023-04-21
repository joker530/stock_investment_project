# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 11:06:20 2023

@author: Administrator
"""
# %% 导入必要的
from datetime import datetime
import dateutil
import pandas as pd
from enum import Enum  #导入枚举库
# %% 设立全局变量G
class G:
    pass
# %% 上下文数据，定义了一个Context类和一个初始化的方法
class Context:
    def __init__(self, cash, start_date, end_date, trade_cal):
        
        start_date = datetime.strptime(start_date, '%Y%m%d')
        end_date = datetime.strptime(end_date, '%Y%m%d')
        # 资金
        self.cash = cash
        # 开始时间
        self.start_date = start_date.strftime('%Y-%m-%d')
        # 结束时间
        self.end_date = end_date.strftime('%Y-%m-%d')
        # 持仓标的信息
        self.positions = {}
        # 基准
        self.benchmark = None
        # 股票池
        self.universe = None
        #  筛出在信息表中的日期
        self.date_range = trade_cal[(trade_cal['is_open'] == 1) &
                            (trade_cal['cal_date'] >= str(self.start_date)) &
                            (trade_cal['cal_date'] <= str(self.end_date))]['cal_date'].values
        # 获得最近的一个交易日的日期
        #today=date.today()
        #last_tradeday=trade_cal[(trade_cal['is_open'] == 1) & (trade_cal['cal_date'] <= str(today))]['cal_date'].values[-1]
        self.dt = dateutil.parser.parse(str(start_date))   #dateutil.parser.parse(str(last_tradeday))
# %% 下单类Order,用于记录下单的操作
class Order:
    def __init__(self, order_type: str, price: float, quantity: int, long: bool, status):
        self.order_type = order_type
        self.price = price
        self.quantity = quantity
        self.long = long
        self.status=status            #这里输入的是像OrderStatus.open，这种

    def cancel(self, quantity: int):
        if quantity > self.quantity:
            raise ValueError("Cannot cancel more than open quantity!")
        self.quantity -= quantity   #这个操作相当于卖出部分仓位
    @property         #这是一个装饰器，这样不用输入参数就能显示对象的总价值了
    def value(self):
        return self.price * self.quantity
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
# %% 定义一个类用于表示下单的类型，输入订单的数量，订单的类型，挂单的价格和止损单的触发价格
class OrderStyle:
    def __init__(self, amount: float, style: str, limit_price: float = None, stop_price: float = None, trailing_percent: float = None):
        self.amount = amount  # 订单数量
        self.style = style  # 订单类型，一般为'limit'和'market'两种
        self.limit_price = limit_price  # 限价单价格
        self.stop_price = stop_price  # 止损单触发价格
        self.trailing_percent = trailing_percent  # 追踪止损单追踪百分比

    def __repr__(self):
        """返回 OrderStyle 对象的字符串表示形式"""
        return f"OrderStyle(amount={self.amount}, style='{self.style}', limit_price={self.limit_price}, stop_price={self.stop_price}, trailing_percent={self.trailing_percent})"
# %% 市价单的类
class MarketOrderStyle(OrderStyle):  
    def __init__(self, current_price, limit_price=None):
        super().__init__(limit_price=limit_price, style='market')
        self.current_price=current_price

    def __repr__(self):
        """返回 MarketOrderStyle 对象的字符串表示形式"""
        return f"MarketOrderStyle(amount={self.amount})"

# %% 订单的交易记录，用于记录每一条交易的信息，注意是已经成交的
class Trade:
    def __init__(self,order_id:int,trade_time,code:str,price:float,amount:int,long=True):
        self.order_id=order_id   #记录Trade记录的id号
        self.trade_time=trade_time
        self.code=code
        self.price=price
        self.amount=amount
        self.long=long
    def __repr__(self):   #用于定义显示的
        """返回 Trade 对象的字符串表示形式"""
        return f"Trade(order_id={self.order_id}, trade_time='{self.trade_time}', code='{self.code}', price={self.price}, amount={self.amount}, long={self.long})"
# %% 订单的列表
class TradeList:
    def __init__(self):
        self.trades = []

    def add_trade(self, trade: Trade) -> None: #->None表示这个方法没有返回值
        """添加一条 Trade 记录"""
        self.trades.append(trade)

    def remove_trade(self, trade: Trade) -> None:
        """移除一条 Trade 记录"""
        self.trades.remove(trade)

    def get_trades(self) -> list:   #这个方法返回一个列表的数据类型
        """获取所有 Trade 记录"""
        return self.trades

    def get_trade_by_id(self, order_id: int):
        """根据 ID 号获取指定的 Trade 记录"""
        for trade in self.trades:
            if trade.order_id == order_id:
                return trade
        return None
# %% 定义一个Position类用于存储单个标的的仓位信息
class Position:
    def __init__(self, code: str, quantity: int, average_cost: float, long: bool):
        self.code = code
        self.quantity = quantity
        self.average_cost = average_cost
        self.long = long      #long属性用来区分多空方向
        self.market_value = quantity * average_cost if long else -quantity * average_cost
        self.cost_basis = self.market_value
        
    def place_order(self, order_type: str, price: float, quantity: int, long: bool):#下单操作，注意还没买入
        if long != self.long:
            raise ValueError("Order direction is different from position direction!")
        if order_type not in ["limit", "market"]:         #order_Type有限价单和市价单之分
            raise ValueError(f"Invalid order type {order_type}!")
        order_value = price * quantity
        if order_type == "limit" and order_value > self.market_value:
            raise ValueError("Not enough market value to place limit order!")
        self.open_orders[order_type].append(Order(order_type, price, quantity, long))
        
    def remove_order(self, order_type: str, price: float, quantity: int):  #取消下单，只有在还未成交时才能成功
        if order_type not in ["limit", "market"]:
            raise ValueError(f"Invalid order type {order_type}!")
        orders = self.open_orders[order_type]
        for i in range(len(orders)):
            order = orders[i]
            if order.price == price and order.quantity == quantity:
                self.open_orders[order_type].pop(i)
                return
        raise ValueError(f"No such order for price {price} and quantity {quantity} found!")
        
    def partial_cancel_order(self, order_type: str, price: float, quantity: int):  #取消部分下单的仓位
        if order_type not in ["limit", "market"]:
            raise ValueError(f"Invalid order type {order_type}!")
        orders = self.open_orders[order_type]
        for i in range(len(orders)):
            order = orders[i]
            if order.price == price and order.quantity >= quantity:
                order.cancel(quantity)   #调用Order类里面的内设函数
                return
        raise ValueError(f"No such order for price {price} and quantity {quantity} found!")
    
    def update_market_value(self, price: float): #输入现价更新市值
        self.market_value = self.quantity * price if self.long else -self.quantity * price
    
    def close(self, quantity: int, price: float):  #以一定的数量和价格进行平仓
        if quantity > self.quantity: #没有足够的仓位进行这个数量的平仓
            raise ValueError("Not enough quantity to close position!")
        if self.long:
            pnl = quantity * (price - self.average_cost)  #多头平仓
        else:
            pnl = quantity * (self.average_cost - price)  #空头平仓
        self.quantity -= quantity   #降低持仓的标的数量
        self.market_value = self.quantity * self.average_cost if self.long else -self.quantity * self.average_cost

    @property
    def value(self):  #输出现有持仓外加挂单的总价值
        return self.market_value + sum([order.value for type in self.open_orders for order in self.open_orders[type]])
# %% 建立一个子账户的类，一个人可以拥有多个子账户
class SubPortfolio:
    def __init__(self, inout_cash: float, margin=1):  #股票和基金的保证金都为100%
        self.inout_cash = inout_cash   #累积出入金,等于你总共投进去的钱
        self.available_cash = inout_cash  #初始化资金等于初始入金
        self.transferable_cash = inout_cash #可取资金
        self.locked_cash = 0.0  #挂单锁住资金
        self.margin = margin
        self.positions = {}
        self.long_positions = {}
        self.short_positions = {}
        self.total_value = inout_cash  #持仓价值加手里现金的价值
        self.returns = 0.0    #计算当日相当于前日的收益率
        self.starting_cash = 0+inout_cash  #这里设置初始没充钱时为0
        self.positions_value = 0.0  #持仓目前的市场价值
        
    def add_position(self, code: str, quantity: int, price: float, long: bool):  #这个函数一般只在出现了新的position时才调用，不然还时用position内的内置函数更新比较好
        position = Position(code, quantity, price, long)
        self.positions[code].append(position)
        if long:
            self.long_positions[code] = position   #往字典中添加元素，position为Position类
        else:
            self.short_positions[code] = position
        self._update_account_info(position.market_value, position.cost_basis)
        
    def remove_position(self, code: str, quantity: int, price: float, long: bool):
        if code not in self.positions:  #持仓中没有要平仓的股票
            raise ValueError(f"No such position for code {code} found!")
        positions = self.positions[code]
        open_qty = sum(p.quantity for p in positions)
        if open_qty < quantity:
            raise ValueError(f"Not enough quantity {open_qty} left for code {code}!")
        target_qty = quantity
        for position in positions:
            if target_qty <= 0:
                break
            if position.quantity <= target_qty:  #卖出该标的的全部持仓
                self._remove_position(position, code)
                target_qty -= position.quantity
            else:
                self._partial_close_position(position, code, target_qty, price, long)  #卖出该标的的部分持仓
                target_qty = 0
    
    def _remove_position(self, position: Position, code: str):  #将该标的的持仓全部卖出
        self.positions[code].remove(position)
        if position.long:
            del self.long_positions[code]   #删除多头持仓
        else:
            del self.short_positions[code]  #删除空头持仓
        self._update_account_info(-position.market_value, -position.cost_basis)
        
    def _partial_close_position(self, position: Position, code: str, quantity: int, price: float, long: bool):
        if position.long and not long or not position.long and long:  #如果做多做空方向不同则报错
            raise ValueError(f"Cannot partial close a position with different long/short direction!")
        if position.quantity < quantity:
            raise ValueError(f"Not enough quantity {position.quantity} left for code {code}!")  #持仓标的不足再次报错
        pnl = quantity * (price - position.average_cost)  #计算这个持仓标的卖出部分的损益
        position.close(quantity, price)   #以这个价格和这个数量进行平仓
        self.available_cash += pnl        #由于available_cash是包含卖出后增加的可用资金的，所以这里对原先的可用资金进行更新，重新算上损益
        self.transferable_cash += pnl
        self.locked_cash -= pnl
        self._update_account_info(pnl, -pnl)
        
    def _update_account_info(self, market_value: float, cost_basis: float):
        self.total_value += market_value
        self.positions_value += market_value
        self.available_cash -= cost_basis
        self.transferable_cash = self.available_cash + self.positions_value * self.margin
        self.returns = (self.total_value + self.inout_cash - self.starting_cash) / self.starting_cash
    
    def place_order(self, order_type: str, code: str, price: float, quantity: int, long: bool):
        if order_type not in ["limit", "market"]:
            raise ValueError(f"Invalid order type {order_type}!")
        if long:
            positions = self.long_positions
        else:
            positions = self.short_positions
        if code not in positions:
            raise ValueError(f"No such position for code {code} found!")
        position = positions[code]
        market_value = position.market_value
        order_value = price * quantity
        if order_type == "limit":
            if long and self.available_cash < order_value or not long and self.positions_value < order_value:
                raise ValueError("Not enough available cash/positions value to place limit order!")
            self.locked_cash += order_value
        elif order_type == "market":
            if long and self.available_cash < market_value or not long and self.positions_value < market_value:
                raise ValueError("Not enough available cash/positions value to place market order!")
            self.locked_cash += market_value
        position.place_order(order_type, price, quantity, long)
        
    def cancel_order(self, order_type: str, code: str, price: float, quantity: int, long: bool):  #取消账户中的某一订单
        if long:
            positions = self.long_positions
        else:
            positions = self.short_positions
        if code not in positions:
            raise ValueError(f"No such position for code {code} found!")
        position = positions[code]
        orders = position.open_orders[order_type]
        remaining_qty = quantity
        for i in range(len(orders)):
            if remaining_qty <= 0:
                break
            order = orders[i]
            if order.price != price:
                continue
            if order.quantity <= remaining_qty:
                remaining_qty -= order.quantity
                position.remove_order(order_type, order.price, order.quantity)
                self.locked_cash -= order.value
            else:
                position.partial_cancel_order(order_type, order.price, remaining_qty)
                self.locked_cash -= remaining_qty * order.price
                remaining_qty = 0

    def update_market_value(self, code: str, price: float):  #更新账户的总市值
        if code not in self.positions:
            raise ValueError(f"No such position for code {code} found!")
        for position in self.positions[code]:
            position.update_market_value(price)

    def deposit(self, amount: float):  #显示账户的现有资金
        self.inout_cash += amount
        self.available_cash += amount
        self.transferable_cash += amount

    def withdraw(self, amount: float):  #用于从账户中提取现金
        if self.available_cash < amount:
            raise ValueError("Not enough available cash to withdraw!")
        self.inout_cash -= amount
        self.available_cash -= amount
        self.transferable_cash -= amount
# %%  用于存储某一标的在某一段时间内的情况，可以考接口进行生成
class SecurityUnitData:  
    def __init__(self, capitalization, turnover_ratio, market_unit, circulating_capitalization, total_capitalization, close_price, volume, date):
        self.capitalization = capitalization  #股票流通股本
        self.turnover_ratio = turnover_ratio  #股票周转率
        self.market_unit = market_unit  #当前股票的市场单位
        self.circulating_capitalization = circulating_capitalization  #流通市值，单位为元
        self.total_capitalization = total_capitalization  #总市值，单位为元
        self.close_price = close_price   #收盘价，单位为元
        self.volume = volume  #成交价，单位为股
        self.date = date   #日期，类如20230705
    
    def to_dict(self):   #返回一个包含这个类所有信息的一个字典
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
    
    def to_df(self):    #输出一个数据表
        import pandas as pd
        return pd.DataFrame([self.to_dict()])
    
    def show(self):   #打印这个类的所有信息
        print("SecurityUnitData:\n")
        print(f"  Date: {self.date}")
        print(f"  Capitalization: {self.capitalization}")
        print(f"  Turnover Ratio: {self.turnover_ratio}")
        print(f"  Market Unit: {self.market_unit}")
        print(f"  Circulating Capitalization: {self.circulating_capitalization}")
        print(f"  Total Capitalization: {self.total_capitalization}")
        print(f"  Close Price: {self.close_price}")
        print(f"  Volume: {self.volume}")
# %% 定义Tick类，包含一只标的当前的盘面信息
class Tick:
    def __init__(self, code, datetime, current, open, high, low, volume, money, position=0, a1_v=0, a2_v=0, 
                 a3_v=0, a4_v=0, a5_v=0, a1_p=0, a2_p=0, a3_p=0, a4_p=0, a5_p=0, b1_v=0, b2_v=0, 
                 b3_v=0, b4_v=0, b5_v=0, b1_p=0, b2_p=0, b3_p=0, b4_p=0, b5_p=0):
        self.code = code
        self.datetime = datetime
        self.current = float(current)
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.volume = float(volume)
        self.money = float(money)
        self.position = float(position)
        self.a1_v = float(a1_v)   #从卖一到卖五的订单量，到时候要写一个爬虫生成这个对象
        self.a2_v = float(a2_v)
        self.a3_v = float(a3_v)
        self.a4_v = float(a4_v)
        self.a5_v = float(a5_v)
        self.a1_p = float(a1_p)    #卖一到卖五的价格
        self.a2_p = float(a2_p)
        self.a3_p = float(a3_p)
        self.a4_p = float(a4_p)
        self.a5_p = float(a5_p)
        self.b1_v = float(b1_v)  #买一到买五的订单量
        self.b2_v = float(b2_v)
        self.b3_v = float(b3_v)
        self.b4_v = float(b4_v)
        self.b5_v = float(b5_v)
        self.b1_p = float(b1_p)  #买一到买五的订单价格
        self.b2_p = float(b2_p)
        self.b3_p = float(b3_p)
        self.b4_p = float(b4_p)
        self.b5_p = float(b5_p)
# %% 定义一个事件对象Event
class Event:
    def __init__(self, event_type: str, time: datetime, sec_code: str):
        self.event_type = event_type  # 事件类型
        self.time = time  # 时间戳
        self.sec_code = sec_code  # 相关股票的代码

    @property
    def current(self):
        """获取当前价格"""
        pass

    @property
    def volume(self):
        """获取成交量"""
        pass

    @property
    def high(self):
        """获取最高价"""
        pass

    @property
    def low(self):
        """获取最低价"""
        pass

    @property
    def open(self):
        """获取开盘价"""
        pass

    @property
    def close(self):
        """获取收盘价"""
        pass
        

