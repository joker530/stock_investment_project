# 这个函数用于设置股票池
import akshare as ak

__all__ = ["set_universe"]


def set_universe(context, type="000300", stock_list=None):
    if type.isdigit():  # 如果全是数字则筛选对应的成分股
        stocks_pool = ak.index_stock_cons(symbol=type)
        lst = list(stocks_pool['品种代码'])   # 代码格式为纯数字字符串，类似”601127“
        context.universe = lst
    elif type == 'other':
        context.universe = stock_list
    else:
        raise TypeError("设置股票池的参数出错")
