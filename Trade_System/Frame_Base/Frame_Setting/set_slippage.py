# 这个函数用于设置回测或者模拟框架的滑点,这个用于子账户层面
import sys
sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform')
from Trade_System.Class_Base.Slippage import *
__all__=["set_slippage"]
'''  固定滑点设置有如下三类

固定值： 这个价差可以是一个固定的值(比如0.02元, 交易时加减0.01元), 设定方式为：FixedSlippage(0.02)
百分比： 这个价差可以是是当时价格的一个百分比(比如0.2%, 交易时加减当时价格的0.1%), 设定方式为：PriceRelatedSlippage(0.002)
跳数（期货专用，双边）: 这个价差可以是合约的价格变动单位（跳数），比如2跳，设定方式为： StepRelatedSlippage(2)；滑点为小数时，向下取整，例如设置为3跳，单边1.5，向下取整为1跳。
'''
def set_slippage(context, Type:str, index=0,num=None,step=None,percents=None,const=None):
    Sp = context.Portfolio.Subportfolios[index]   # 默认是第一个子账户进行设置
    if Type=="Fixed":
        if const==None:
            Sp.slippage = FixedSlippage()
        else:
            Sp.slippage = FixedSlippage(const)
    elif Type=="Price":
        if percents==None:
            Sp.slippage = PriceRelatedSlippage()
        else:
            Sp.slippage = PriceRelatedSlippage(percents)
    elif Type=="Step":
        if num==None or step==None:
            Sp.slippage = StepRelatedSlippage()
        else:
            Sp.slippage = StepRelatedSlippage(step, num)
    else:
        raise TypeError("目前不支持该类型滑点的设置")

