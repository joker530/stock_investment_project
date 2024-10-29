# -*- coding: utf-8 -*-
# tick表示的含义是价格和成交量的最小变动单位。
# %% 导入库
import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

from Attain_Data.Share_Info.Stock_Info_Collector import *
from datetime import date


# %% 定义Tick类，包含一只标的当前的盘面信息,这个对象一般是用在实时交易的情况，回测模式一般用不上,以代码为主键
class Tick:
    def __init__(self, code, position=0, a1_v=0, a2_v=0,
                 a3_v=0, a4_v=0, a5_v=0, a1_p=0, a2_p=0, a3_p=0, a4_p=0, a5_p=0, b1_v=0, b2_v=0,
                 b3_v=0, b4_v=0, b5_v=0, b1_p=0, b2_p=0, b3_p=0, b4_p=0, b5_p=0, kind='stock'):
        self.kind = kind
        self.code = code
        if self.kind == "stock":  # 如果是股票类型的话
            self.sic = Stock_Info_Collector(self.code)
            df = self.sic.get_current_datas()  # 获取当前标的交易信息
            DF = self.sic.get_baojia()['value']  # 获得当前的报价信息
            self.datetime = date.today()
            self.current = float(df['最新价'])
            self.open = float(df['今开'])
            self.high = float(df['最高'])
            self.low = float(df['最低'])
            self.volume = float(df['成交量'])  # 截止到目前为止的成交量
            self.money = float(df['成交额'])  # 截止到目前为止的成交额
            self.position = float(position)  # 期货专用数据
            self.a1_v = float(DF[9])  # 从卖一到卖五的订单量，到时候要写一个爬虫生成这个对象
            self.a2_v = float(DF[7])
            self.a3_v = float(DF[5])
            self.a4_v = float(DF[3])
            self.a5_v = float(DF[1])
            self.a1_p = float(DF[8])  # 卖一到卖五的价格
            self.a2_p = float(DF[6])
            self.a3_p = float(DF[4])
            self.a4_p = float(DF[2])
            self.a5_p = float(DF[0])
            self.b1_v = float(DF[11])  # 买一到买五的订单量
            self.b2_v = float(DF[13])
            self.b3_v = float(DF[15])
            self.b4_v = float(DF[17])
            self.b5_v = float(DF[19])
            self.b1_p = float(DF[10])  # 买一到买五的订单价格
            self.b2_p = float(DF[12])
            self.b3_p = float(DF[14])
            self.b4_p = float(DF[16])
            self.b5_p = float(DF[18])

    def update(self):  # 这个方法用于更新tick对象
        if self.kind == "stock":  # 如果是股票类型的话
            df = self.sic.get_current_datas()  # 获取当前标的交易信息
            DF = self.sic.get_baojia()['value']  # 获得当前的报价信息
            self.datetime = date.today()
            self.current = float(df['最新价'])
            self.open = float(df['今开'])
            self.high = float(df['最高'])
            self.low = float(df['最低'])
            self.volume = float(df['成交量'])  # 截止到目前为止的成交量
            self.money = float(df['成交额'])  # 截止到目前为止的成交额
            self.a1_v = float(DF[9])  # 从卖一到卖五的订单量，到时候要写一个爬虫生成这个对象
            self.a2_v = float(DF[7])
            self.a3_v = float(DF[5])
            self.a4_v = float(DF[3])
            self.a5_v = float(DF[1])
            self.a1_p = float(DF[8])  # 卖一到卖五的价格
            self.a2_p = float(DF[6])
            self.a3_p = float(DF[4])
            self.a4_p = float(DF[2])
            self.a5_p = float(DF[0])
            self.b1_v = float(DF[11])  # 买一到买五的订单量
            self.b2_v = float(DF[13])
            self.b3_v = float(DF[15])
            self.b4_v = float(DF[17])
            self.b5_v = float(DF[19])
            self.b1_p = float(DF[10])  # 买一到买五的订单价格
            self.b2_p = float(DF[12])
            self.b3_p = float(DF[14])
            self.b4_p = float(DF[16])
            self.b5_p = float(DF[18])
