# 这个脚本专门用于定义滑点的三种类型
'''
固定滑点设置有如下三类

固定值： 这个价差可以是一个固定的值(比如0.02元, 交易时加减0.01元), 设定方式为：FixedSlippage(0.02)
百分比： 这个价差可以是是当时价格的一个百分比(比如0.2%, 交易时加减当时价格的0.1%), 设定方式为：PriceRelatedSlippage(0.002)
跳数（期货专用，双边）: 这个价差可以是合约的价格变动单位（跳数），比如2跳，设定方式为： StepRelatedSlippage(2)；
滑点为小数时，向下取整，例如设置为3跳，单边1.5，向下取整为1跳。
'''
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

__all__ = ['FixedSlippage', 'PriceRelatedSlippage', 'StepRelatedSlippage']  # 分别是固定值、百分比和跳数


class FixedSlippage:
    def __init__(self, const=0.02):
        self.FixedSlippage = const

    def get_slippage(self, type="buy", price=None):
        if type == "buy":
            return self.FixedSlippage
        elif type == "sell":
            return -self.FixedSlippage


class PriceRelatedSlippage:
    def __init__(self, percents=0.002):
        self.percents = percents

    def get_slippage(self, price, type="buy"):
        slippage = max(self.percents * price, 0.01)
        if type == "buy":
            return slippage
        elif type == "sell":
            return -slippage


class StepRelatedSlippage:
    def __init__(self, step=5, num=2):
        self.step = step
        self.jump_num = num

    def get_slippage(self, price, type="buy"):
        slippage = self.jump_num * self.step
        if type == "buy":
            return slippage
        elif type == "sell":
            return -slippage
