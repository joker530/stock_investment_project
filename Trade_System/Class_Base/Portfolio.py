# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 11:06:20 2023

@author: Administrator
"""
##
# %%
import sys
import os
Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

##
import time
import datetime
from Trade_System.Class_Base.SubPortfolio import *
from utils.date_handing import *  # 导入日期格式处理工具

# %%
__all__ = ["Portfolio"]


# %% 建立一个总账户系统，用于统计所有子账户的关键信息，主要意义在于统计而不是实际操作层面。但是未打_的函数都必须是原子操作。
class Portfolio:
    def __init__(self, recharge_limit: float):  # 这里的外围类指的是context类,recharge_limit是目前手里可以充钱的上限
        self.recharge_limit = recharge_limit       # 主账户目前手里可以充钱的上限，不随增删账户改变
        self.remaining_recharge = recharge_limit   # 主账户剩余的可充值金额，不随增删账户改变

        self.inout_cash = 0  # 累计出入金, 比如初始资金 1000, 后来转移出去 100, 则这个值是 1000 - 100,转入和转出子账户的才是出入金
        self.available_cash = 0  # 可用资金, 可用来购买证券的资金
        self.transferable_cash = 0  # 可取资金, 即可以提现的资金, 不包括今日卖出证券所得资金
        self.positions = {}         # 所有仓位的集合
        self.total_value = 0        # 总的权益, 包括现金, 保证金(期货)或者仓位(股票)的总价值, 可用来计算收益
        self.total_liability = 0    # 总的负债，一般在融资账户中会有体现
        self.net_value = self.total_value - self.total_liability
        self.last_net_value = self.net_value  # 这个用于记录账户前一天的净资产
        self.returns = 0           # 总权益的累计收益比率；（当前总资产- 初始本金投入- 总负债） / 累计出入金；
        self.positions_value = 0   # 持仓价值

        self.Subportfolios = list()  # 专门用于存放子账户的列表，每次增删账户的时候都会在这里操作一下

        self.create_time = time.time()
        self.current_trade_date = datetime.date(1990, 1, 1)  # 用这个变量记录当前交易日的时间，在before_trading_start时会重新赋值一次，这个有问题

    def increase_limit(self, amount):  # 使用这个函数提高充值上限
        self.recharge_limit += amount
        self.remaining_recharge += amount

    def decrease_limit(self, amount):  # 使用这个函数降低充值上限
        self.recharge_limit -= amount
        self.remaining_recharge -= amount

    def get_Subportfolio_by_name(self, name: str) -> SubPortfolio:   # 根据名字返回一个Subportfolio对象
        for i in range(len(self.Subportfolios)):
            if self.Subportfolios[i].name == name:
                return self.Subportfolios[i]
        raise ValueError(f"没有名称为{name}的子账户，无法返回，请重新确认！")

    def create_new_SubPortfolio(self, mother_cash, type="stock", name="我的股票账户"):  # 创建一个新的子账户
        new_SubPortfolio = SubPortfolio(master=self, mother_cash=mother_cash, type=type, name=name)
        if (self.remaining_recharge - new_SubPortfolio.net_value) < 0:
            raise TypeError(f"无法创建子账户,当前主账户剩余可充值金额: {self.remaining_recharge}")
        for i in range(len(self.Subportfolios)):
            if self.Subportfolios[i].name == name:
                raise ValueError(f"名称为{name}的账户已存在，请重新命名添加账户，谢谢！")
        self.Subportfolios.append(new_SubPortfolio)
        self.update_Portfolio_info()

    def remove_SubPortfolio_Byname(self, name: str):  # 输入账户的名称删去子账户
        for i in range(len(self.Subportfolios)):
            if self.Subportfolios[i].name == name:
                num = i
                self._update_global_info(num, False)
                print(f"名称为：{name}的子账户已经删除")
                break
        self.update_Portfolio_info()

    def update_Portfolio_info(self):  # 根据已有的子账户数据进行手动更新
        self._restart_Portfolio_info()  # 先初始化
        for i in range(len(self.Subportfolios)):
            self._update_global_info(num=i, is_add=True)  # 逐个进行累加

    def update_date_info(self, date: str):   # 用这个函数更新账户的日期信息
        self.dt = long_datestr_to_dd(str(date))
        self.last_net_value = self.net_value
        for i in range(len(self.Subportfolios)):
            self.Subportfolios[i].update_date_info(date=date)
        pass

    def update_price_info(self):        # 每个交易日结尾被Context对象调用，用于更新收盘价和回报率
        for i in range(len(self.Subportfolios)):
            self.Subportfolios[i].update_price_info()
        self._update_returns()  # 更新总回报率

    def _merge_dicts(self, dict1, dict2) -> dict:  # 专门用于字典合并的函数
        merged_dict = {}
        for key in dict1.keys() | dict2.keys():
            if key in dict1 and key in dict2:
                merged_dict[key] = [dict1[key], dict2[key]]
            elif key in dict1:
                merged_dict[key] = dict1[key]
            else:
                merged_dict[key] = dict2[key]
        return merged_dict

    def _restart_Portfolio_info(self):  # 先初始化再统计各个子账户
        self.inout_cash = 0
        self.available_cash = 0
        self.transferable_cash = 0
        self.positions = {}

        self.total_value = 0
        self.total_liability = 0
        self.net_value = 0  # 这里有问题

        self.returns = 0
        self.positions_value = 0

        self.remaining_recharge = self.recharge_limit

    def _update_global_info(self, num=-1, is_add=True):
        if is_add:
            SubPortfolio = self.Subportfolios[num]
            self.inout_cash += SubPortfolio.inout_cash
            self.available_cash += SubPortfolio.available_cash
            self.transferable_cash += SubPortfolio.transferable_cash
            self.positions = self._merge_dicts(self.positions, SubPortfolio.positions)  # 添加这个子账户原有的仓位信息

            self.total_value += SubPortfolio.total_value
            self.total_liability += SubPortfolio.total_liability
            self.net_value += SubPortfolio.net_value

            self.positions_value += SubPortfolio.positions_value
            self.remaining_recharge = self.remaining_recharge - SubPortfolio.inout_cash
        else:
            del self.Subportfolios[num]  # 删除子账户

    def _update_returns(self):
        self.returns = (self.net_value - self.last_net_value) / self.last_net_value

    def __repr__(self):  # 用于定义显示的
        """返回 Portfolio 对象的字符串表示形式"""
        return f"Portfolio(remaining_recharge={self.remaining_recharge}, inout_cash={self.inout_cash}, available_cash='{self.available_cash}', transferable_cash='{self.transferable_cash}', total_value={self.total_value}, total_liability={self.total_liability}, net_value={self.net_value}, returns={self.returns})"


# %%
if __name__ == "__main__":
    a = 1
    P = Portfolio(recharge_limit=300000)
    P.create_new_SubPortfolio(100000, name="account1")
    P.create_new_SubPortfolio(100000, name="account2")
    Sp = P.Subportfolios[0]
    Sp.using_loan(100000, 0.06, 1.5)  # 对第一个子账户使用融资
    print(len(P.Subportfolios))
    print(P.Subportfolios)
    # P.remove_SubPortfolio_Byname("account1")
    # P.remove_SubPortfolio_Byname("account2")
    print(P.Subportfolios[0].name)
    print(P.Subportfolios[1].name)
    print(P)
