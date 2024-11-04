# 这个函数用于设置Context内的基准

__all__ = ["set_benchmark"]


def set_benchmark(context, diction):
    if isinstance(diction, dict):
        if sum(diction.values()) is not 1:
            raise TypeError("所有权重的之和要等于1，请修改权重！")
        else:
            context.benchmark = diction
    elif isinstance(diction, str):
        context.benchmark = dict()
        context.benchmark[diction] = 1
    else:
        raise TypeError("基准参数设置错误")

# 示例1
# set_benchmark(context, '600000')
# 示例2
# set_benchmark(context, {'000001':0.5,'000300':0.3,'600000':0.2})
