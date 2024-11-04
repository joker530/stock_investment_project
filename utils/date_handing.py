# 这个功能模块用于解决日期的各种变化问题
##
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)

from datetime import datetime

__all__ = ["long_to_short_datestr", "short_to_long_datestr", "dd_to_short_datestr", "dd_to_long_datestr",
           "get_date_range_list", "short_datestr_to_dd", "long_datestr_to_dd"]


## 第一种，带横杠的字符串日期向不带横杆的字符串日期转换
def long_to_short_datestr(s: str):
    date_obj = datetime.strptime(s, '%Y-%m-%d')  # 需要经过中间这个转换步骤
    new_date_str = date_obj.strftime('%Y%m%d')
    return new_date_str


## 第二种，不带横杠的字符串日期向带横杆的字符串日期转换
def short_to_long_datestr(s: str):
    date_obj = datetime.strptime(s, '%Y%m%d')  # 需要经过中间这个转换步骤
    new_date_str = date_obj.strftime('%Y-%m-%d')
    return new_date_str


## 第三种，datetime.datetime格式数据转换为不带横杠的日期字符串
def dd_to_short_datestr(date: datetime):
    new_date_str = date.strftime('%Y%m%d')
    return new_date_str


## 第四种，datetime.datetime格式数据转换为带横杠的日期字符串
def dd_to_long_datestr(date: datetime):
    new_date_str = date.strftime('%Y-%m-%d')
    return new_date_str


## 第五种，不带横杠的日期字符串转换为datetime.datetime格式数据
def short_datestr_to_dd(s: str):
    return datetime.strptime(s, '%Y%m%d')


## 第六种，带横杠的日期字符串转换为datetime.datetime格式数据
def long_datestr_to_dd(s: str):
    return datetime.strptime(s, '%Y-%m-%d')


## 根据时间范围筛查csv数据表的日期，并返回一个'numpy.ndarray'数组对象
def get_date_range_list(trade_cal_csv, start_date, end_date):
    date_range = trade_cal_csv[(trade_cal_csv['trade_date'] >= str(start_date)) &
                               (trade_cal_csv['trade_date'] <= str(end_date))]['trade_date'].values
    # 将一个'numpy.ndarray'对象，转换为list对象
    return date_range.tolist()
