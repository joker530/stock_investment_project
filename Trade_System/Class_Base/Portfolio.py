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
from Trade_System.Class_Base.SubPortfolio import *
import time
import datetime

# %%
__all__ = ["Portfolio"]


# %% 建立一个总账户系统，用于统计所有子账户的关键信息，主要意义在于统计而不是实际操作层面。
class Portfolio:
    def __init__(self, mother_cash: float):  # 这里的外围类指的是context类,mother_cash是目前手里可以充钱的上限
        self.mother_cash = mother_cash
        self.mother_left = mother_cash   # 主账户剩余的账户现金
        self.inout_cash = 0  # 累计出入金, 比如初始资金 1000, 后来转移出去 100, 则这个值是 1000 - 100
        self.available_cash = 0  # 可用资金, 可用来购买证券的资金
        self.transferable_cash = 0  # 可取资金, 即可以提现的资金, 不包括今日卖出证券所得资金
        self.locked_cash = 0  # 挂单锁住资金
        self.margin = 1  # 保证金，股票、基金保证金都为100%
        self.positions = {}  # 等同于 long_positions
        self.long_positions = {}  # 多单的仓位, 一个 dict, key 是证券代码, value 是 [Position]对象
        self.short_positions = {}  # 空单的仓位, 一个 dict, key 是证券代码, value 是 [Position]对象
        self.total_value = 0  # 总的权益, 包括现金, 保证金(期货)或者仓位(股票)的总价值, 可用来计算收益
        self.total_liability = 0  # 总的负债，一般在融资账户中会有体现
        self.net_value = self.total_value - self.total_liability
        self.returns = self.net_value / self.mother_cash  # 总权益的累计收益比率；（当前总资产- 初始本金投入- 总负债） / 初始本金；
        self.positions_value = 0  # 持仓价值
        self.Subportfolios = list()
        self.create_time = time.time()
        self.current_trade_date = datetime.date(1990, 1, 1)  # 用这个变量记录当前交易日的时间，在before_trading_start时会重新赋值一次

    def create_new_SubPortfolio(self, inout_cash, margin=1, type="stock", name="我的股票账户"):  # 创建一个新的子账户
        new_SubPortfolio = SubPortfolio(master=self, inout_cash=inout_cash, margin=margin, type=type, name=name)
        if (self.mother_left - new_SubPortfolio.inout_cash) < 0:
            raise TypeError(f"主账户资金不足，无法创建子账户。当前主账户剩余资金为: {self.mother_left}")
        self.Subportfolios.append(new_SubPortfolio)
        self._update_global_info()
        self.update_Portfolio_info()

    def add_SubPortfolio(self, SubPortfolio: SubPortfolio):  # 添加一个子账户,一般是现成的才用添加
        if (self.mother_left - SubPortfolio.inout_cash) < 0:
            raise TypeError(f"主账户资金不足，无法添加子账户。当前主账户剩余资金为: {self.mother_left}")
        self.Subportfolios.append(SubPortfolio)
        self._update_global_info()  # 默认是最后一个子账户
        self.update_Portfolio_info()

    def remove_SubPortfolio(self, SubPortfolio):  # 删去一个子账户
        # self.Subportfolios.remove(SubPortfolio)
        num = self.Subportfolios.index(SubPortfolio)
        self._update_global_info(num, False)
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
        self.restart_Portfolio_info()  # 先初始化
        for i in range(len(self.Subportfolios)):
            self._update_global_info(num=i, is_add=True)  # 逐个进行累加

    def _merge_dicts(self, dict1, dict2):  # 专门用于字典合并的函数
        merged_dict = {}
        for key in dict1.keys() | dict2.keys():
            if key in dict1 and key in dict2:
                merged_dict[key] = [dict1[key], dict2[key]]
            elif key in dict1:
                merged_dict[key] = dict1[key]
            else:
                merged_dict[key] = dict2[key]
        return merged_dict

    def restart_Portfolio_info(self):  # 先初始化再统计各个子账户
        self.margin = 1
        self.inout_cash = 0
        self.available_cash = 0
        self.transferable_cash = 0
        self.locked_cash = 0
        self.positions = {}
        self.long_positions = {}
        self.short_positions = {}
        self.total_value = self.mother_left
        self.returns = 0
        self.positions_value = 0
        self.total_liability = 0
        self.net_value = self.mother_left
        self.mother_left = self.mother_cash

    def _update_global_info(self, num=-1, is_add=True):
        if is_add:
            SubPortfolio = self.Subportfolios[num]
            self.margin = (self.inout_cash * self.margin + SubPortfolio.inout_cash * SubPortfolio.margin) / (
                    self.inout_cash + SubPortfolio.inout_cash)
            self.inout_cash += SubPortfolio.inout_cash
            self.available_cash += SubPortfolio.available_cash
            self.transferable_cash += SubPortfolio.transferable_cash
            self.locked_cash += SubPortfolio.locked_cash
            self.positions = self._merge_dicts(self.positions, SubPortfolio.positions)  # 添加这个子账户原有的仓位信息
            self.long_positions = self._merge_dicts(self.long_positions, SubPortfolio.long_positions)
            self.short_positions = self._merge_dicts(self.short_positions, SubPortfolio.short_positions)
            self.total_value += SubPortfolio.total_value
            self.total_liability += SubPortfolio.total_liability
            self.net_value += SubPortfolio.net_value
            self.returns += SubPortfolio.returns
            self.positions_value += SubPortfolio.positions_value
            self.mother_left = self.mother_left - SubPortfolio.inout_cash
        else:
            del self.Subportfolios[num]  # 删除子账户

    def __repr__(self):  # 用于定义显示的
        """返回 Portfolio 对象的字符串表示形式"""
        return f"Portfolio(mother_left={self.mother_left}, inout_cash={self.inout_cash}, available_cash='{self.available_cash}', transferable_cash='{self.transferable_cash}', total_value={self.total_value}, total_liability={self.total_liability}, net_value={self.net_value}, returns={self.returns})"


# %%
if __name__ == "__main__":
    a = 1
    P = Portfolio(mother_cash=300000)
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
