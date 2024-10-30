# 这个软件包是用来设置策略框架的基本设置的,导入这些方法
import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)  # 将当前文件夹添加到搜索路径

from set_slippage import *
from set_universe import *
from set_benchmark import *
from set_volume_ratio import *
