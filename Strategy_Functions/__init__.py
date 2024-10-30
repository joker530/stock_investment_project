##
# 用于导出用户自己编写的策略

import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)  # 将当前文件夹添加到搜索路径

from SVM import *
