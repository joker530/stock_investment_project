# 这个类用于记录佣金及印花税的详细信息
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

__all__ = ["OrderCost"]
class OrderCost:
    def __init__(self, type="stock"):
        if type == "stock":
            self.open_tax = 0  # 买入印花税
            self.close_tax = 0.001  # 卖出印花税
            self.open_commission = 0.0003  # 买入所需要付的佣金
            self.close_commission = 0.0003  # 卖出所需要负的佣金
            self.close_today_commission = 0  # 平今仓所需要付出的佣金，一般在期货市场中有
            self.min_commission = 5  # 最小要付的佣金
            self.type = type
        elif type == 'future':
            self.open_tax = 0  # 买入印花税
            self.close_tax = 0.00  # 卖出印花税
            self.open_commission = 0.000023  # 买入所需要付的佣金
            self.close_commission = 0.000023  # 卖出所需要负的佣金
            self.close_today_commission = 0.0023  # 平今仓所需要付出的佣金，一般在期货市场中有
            self.min_commission = 0
            self.type = type
        else:
            raise TypeError("目前不支持这种交易品种")

    def buy_fee(self, Order_value):  # 计算买入需要的花费
        return max((self.open_tax + self.open_commission) * Order_value,
                   self.min_commission + self.open_tax * Order_value)

    def sell_fee(self, Order_value):  # 计算卖出需要的花费
        return max((self.open_tax + self.close_commission) * Order_value,
                   self.min_commission + self.close_tax * Order_value)

    def sell_today_fee(self, Order_value):  # 计算今天买入直接平仓需要的花费
        if self.type == 'future':
            return self.close_today_commission * Order_value
        else:
            raise TypeError("当前品种不支持计算即日平仓费用！")

    def __repr__(self):
        return f"OrderCost(open_tax={self.open_tax}, " \
               f"close={self.close_tax}, open_commission={self.open_commission}," \
               f" close_commission={self.close_commission}, " \
               f"close_today_commission={self.close_today_commission}" \
               f"min_commission={self.min_commission})"
