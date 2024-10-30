# 这个函数用于设置最大成交单位比例,相当于限制了单笔订单买入的仓位
__all__ = ["set_volume_ratio"]


def set_volume_ratio(context, rate=1, index=0):
    Sp = context.Portfolio.Subportfolios[index]
    Sp.volume_ratio = rate
