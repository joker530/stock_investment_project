import importlib


def _get_strategy():
    strategy_name = 'Strategy_Functions.ExecutiveBase.Stock_Executive.SVM'  # 模块名字
    try:
        # 动态导入模块
        module = importlib.import_module(strategy_name)
        print(dir(module))  # 打印模块中的所有属性，确认是否有 'initialize'

        # 从模块中获取 'initialize' 属性
        if hasattr(module, 'initialize'):
            return getattr(module, 'initialize')
        else:
            raise AttributeError(f"Module '{strategy_name}' does not have an attribute 'initialize'")
    except ModuleNotFoundError as e:
        print(e)
        raise e
    except AttributeError as e:
        print(e)
        raise e


# 调用函数
try:
    strategy = _get_strategy()
except Exception as e:
    print(f"An error occurred: {e}")