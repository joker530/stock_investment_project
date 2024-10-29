# 这个函数用于设置Context内的基准

__all__ = ["set_benchmark"]


def set_benchmark(context, diction):
    if isinstance(diction, dict):
        context.benchmark = diction
    elif isinstance(diction, str):
        context.benchmark = {}
        context.benchmark[diction] = 1
    else:
        raise TypeError("基准参数设置错误")
