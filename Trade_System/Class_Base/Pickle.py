# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 17:48:11 2023

@author: Administrator
"""
# 这个文件用于定义类的数据压缩和导入的方法
import pickle
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

# %%
__all__ = ["dump_class", "load_class"]


# %%
def dump_class(filename: str, class_name):
    location = Base_dir + '/Trade_System/Pickle_bags/' + filename + '.pkl'
    # location = 'D:/量化投资/交易框架的编写/backtesting_platform/Trade_System/Pickle_bags/' + filename + '.pkl'
    with open(location, "wb") as f:
        pickle.dump(class_name, f)


def load_class(filename: str):
    location = Base_dir + '/Trade_System/Pickle_bags/' + filename + '.pkl'
    # location = 'D:/量化投资/交易框架的编写/backtesting_platform/Trade_System/Pickle_bags/' + filename + '.pkl'
    with open(location, "rb") as f:
        var = pickle.load(f)
    return var