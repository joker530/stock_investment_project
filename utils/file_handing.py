# 这个功能模块用于实现文件的检查、生成、压缩、加载等功能
import os
import sys
import pickle
import importlib

Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)
##
__all__ = ["is_file_here", "dump_class", "load_class", "dynamic_import"]


def is_file_here(filepath):
    """检查给定路径是否是一个存在的文件。"""
    return os.path.isfile(filepath)
    pass


def dump_class(filename: str, class_name):
    """把文件压缩成pkl文件并放在一个指定的地址。"""
    location = Base_dir + '/Datasets/Compressed_Objects/' + filename + '.pkl'
    # location = 'D:/量化投资/交易框架的编写/backtesting_platform/Trade_System/Pickle_bags/' + filename + '.pkl'
    with open(location, "wb") as f:
        pickle.dump(class_name, f)


def load_class(filename: str):
    """根据地址加载pkl文件。"""
    location = Base_dir + '/Datasets/Compressed_Objects/' + filename + '.pkl'
    # location = 'D:/量化投资/交易框架的编写/backtesting_platform/Datasets/Compressed_Objects/Compressed_Strategy/SVM.pkl'
    # print(os.path.exists(location))
    # print(location)
    with open(location, "rb") as f:
        var = pickle.load(f)
    return var


def dynamic_import(module_name):
    # 这个函数用来动态的导入模块,在使用这个函数之前请确认对应的库是否已经添加到路径
    try:
        module = importlib.import_module(name=module_name)  # 其中package是最小父文件
        return module
    except ImportError as e:
        print(f"导入模块 {module_name} 失败: {e}")
        return None
