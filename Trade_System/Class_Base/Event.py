# -*- coding: utf-8 -*-
from datetime import datetime
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(Base_dir)

# %%
__all__ = ["Event"]


# %% 定义一个事件对象Event
class Event:
    def __init__(self, event_type: str, time: datetime, sec_code: str):
        self.event_type = event_type  # 事件类型
        self.time = time  # 时间戳
        self.sec_code = sec_code  # 相关股票的代码

    @property
    def current(self):
        """获取当前价格"""
        pass

    @property
    def volume(self):
        """获取成交量"""
        pass

    @property
    def high(self):
        """获取最高价"""
        pass

    @property
    def low(self):
        """获取最低价"""
        pass

    @property
    def open(self):
        """获取开盘价"""
        pass

    @property
    def close(self):
        """获取收盘价"""
        pass
