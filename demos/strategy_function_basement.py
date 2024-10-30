# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 13:37:46 2023

@author: Administrator
"""
import sys
sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform/trade_frame')
import pandas as pd
import dateutil
import tushare_frame as tf
import matplotlib
import matplotlib.pyplot as plt
import time   # 用于程序调试的运行时间
from datetime import datetime, timedelta
# %% 这个函数用于实现当短期线突破长期线时买入，
# 当长期线突破短期线时卖出的策略，也就是俗称的追涨杀跌
def init_cgcl(short,long,g,context):
    start_date_str = context.start_date   
    start = datetime.strptime(start_date_str, '%Y-%m-%d')
    delta = timedelta(days=(long+90))
    start-=delta
    start = start.strftime('%Y-%m-%d')
    tf.ts_daily(g.security,start,context.end_date)
    
def main_cgcl(short,long,g,context,trade_cal,index=True): #短期均线和长期均线
    # 创建收益数据表
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range), columns=['value'])
    init_value = context.cash
    last_prize = {}
    buy_points = []   #用于存储买卖点
    sell_points = []
    #print(context.date_range)
    for dt in context.date_range:
        #print(context.positions)
        context.dt = dateutil.parser.parse(dt)
        #print(context.dt)
        hist = tf.attribute_history(g.security, long, trade_cal=trade_cal, context=context)
        # short日均线
        #print(hist)
        ma_short = hist['close'][-short:].mean()
        #print(ma_short)
        # long日均线
        ma_long = hist['close'].mean()
        #print(ma_long)
        if (ma_short > ma_long)*index and g.security not in context.positions:
            tf.order_value(g.security, context.cash, context)
            buy_points.append((dt, 0))
            # 如果5日均线小于30日均线, 并且持仓, 则清仓
        elif (ma_short < ma_long)*index and g.security in context.positions:
            #print(vars(context))
            tf.order_target_value(g.security, 0 , context) 
            sell_points.append((dt, 0))
        value = context.cash   #每次记录剩余的钱
        for stock in context.positions:
            today_data = tf.get_today_data(stock,context)
            # 停牌
            if len(today_data) == 0:
                # 停牌前一交易日股票价格
                p = last_prize[stock]
            else:
                p = today_data['open']
                # 存储为停牌前一交易日股票价格
                last_prize[stock] = p
            value += p * context.positions[stock]
        plt_df.loc[dt, 'value'] = value
    # fname 为你的字体库路径和字体名
    # 图形中文显示， Matplotlib 默认情况不支持中文
    # 收益率
    plt_df['ratio'] = (plt_df['value'] - init_value) / init_value
    for i in range(len(buy_points)):
        lst = list(buy_points[i])
        lst[1]=plt_df.loc[buy_points[i][0],'ratio']
        buy_points[i]=tuple(lst)
    for i in range(len(sell_points)):
        lst = list(sell_points[i])
        lst[1]=plt_df.loc[sell_points[i][0],'ratio']
        sell_points[i]=tuple(lst)
        
    bm_df = tf.attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['open'][0]
    # 基准收益率
    plt_df['benckmark_ratio'] = (bm_df['open'] - bm_init) / bm_init
    return plt_df,buy_points,sell_points

def paint_cgcl(plt_df, buy_points, sell_points, xlabel, ylabel):
    zhfont1 = matplotlib.font_manager.FontProperties(fname="G:/ai/量化投资/交易框架的编写/青鸟华光简细圆.TTF")
    plt.title("python简单回测框架", fontproperties=zhfont1)
    plt.plot(plt_df['ratio'], label="ratio")
# 绘制基准收益率曲线
    plt.plot(plt_df['benckmark_ratio'], label="benckmark_ratio")
    x = [d for d, v in buy_points]
    y = [v for d, v in buy_points]
    plt.scatter(x, y, marker='o', facecolors='none', edgecolors='b')
    x = [d for d, v in sell_points]
    y = [v for d, v in sell_points]
    plt.scatter(x, y, marker='o', facecolors='none', edgecolors='r')
# fontproperties 设置中文显示用字体，fontsize 设置字体大小
    plt.xlabel(xlabel, fontproperties=zhfont1)
    plt.ylabel(ylabel, fontproperties=zhfont1)
# x坐标斜率
    plt.xticks(rotation=46)
# 添加图注
    plt.legend()
# 显示
    plt.show()
    
# %% 
