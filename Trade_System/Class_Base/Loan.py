# -*- coding: utf-8 -*-
"""
Created on Sat May  6 19:18:48 2023

@author: Administrator
"""
##
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

__all__ = ["Loan"]
##

# %%
# 这个类是融资融券类，是算做子账户的子级
class Loan:
    def __init__(self, principal, rate, term, load_type="cash"):
        self.principal = principal  # 贷款本金
        self.rate = rate  # 年利率
        self.term = term  # 贷款期限（单位：年）
        if load_type not in ["cash", "sec"]:
            raise ValueError("没有这种贷款类型")
        self.load_type = load_type  # 贷款种类，分为融资和融券，融资为cash，融券为sec

    def monthly_payment(self):
        """计算每月还款额"""
        r = self.rate / 12  # 月利率
        n = self.term * 12  # 还款期数
        return self.principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    def total_interest(self):
        """计算总利息"""
        return self.monthly_payment() * self.term * 12 - self.principal

    def total_cost(self):
        """计算总成本（本金+利息）"""
        return self.monthly_payment() * self.term * 12

    def __repr__(self):
        return f"Loan(principal={self.principal}, rate={self.rate}, term={self.term}, load_type='{self.load_type}')"


# %%
if __name__ == "__main__":
    # 创建一个新的贷款对象
    loan = Loan(100000, 0.05, 10)

    # 计算每月还款额
    monthly_payment = loan.monthly_payment()
    print("每月还款额：", monthly_payment)

    # 计算总利息
    total_interest = loan.total_interest()
    print("总利息：", total_interest)

    # 计算总成本
    total_cost = loan.total_cost()
    print("总成本：", total_cost)
