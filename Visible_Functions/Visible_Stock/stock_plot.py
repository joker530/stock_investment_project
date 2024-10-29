# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 15:25:01 2023

@author: Administrator
"""
import matplotlib.pyplot as plt
import pandas as pd
import os
import talib
import mplfinance as mpf
import numpy as np

# %%
__all__ = ["stock_plot"]


# %% 定义一个类，专门用来画股票的K线
class stock_plot(object):
    def __init__(self, kind="日K"):
        self.kind = kind
        self.data = pd.DataFrame()
        self.ap = []  # 用于存储额外添加其它绘图

    # 输入一个数据表的名称，返回一个处理过后的pd表格
    # 绘图前得先有csv数据，具体获得方法在Stock_Info_Collector.py里面
    def datas_day_op(self, filename='002230.SZ.csv'):
        title = filename.split(".")
        self.title = title[0] + title[1]
        data = pd.read_csv("D:/量化投资/交易框架的编写/backtesting_platform/Data_Table/K_Lines/datas_daily/" + filename)
        # 获取必要的数据
        print(data)
        data = data[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '涨跌额', '涨跌幅', '换手率']]
        # 重命名
        data.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'change', 'pct_chg',
                        'turnover_rate']
        data["pre_close"] = data["close"] - data["change"]   # 计算各个交易日前一个交易日的收盘价
        data['upper_lim'] = np.round(data['pre_close'] * 1.10)  # 上轨线，也就是乘以一定比率，比率可调且大于1
        data['lower_lim'] = np.round(data['pre_close'] * 0.90)  # 下轨线，也就是乘以一定比率，比率可调且小于1
        data['average'] = np.round((data['high'] + data['low']) / 2)  # 日平均价格，最高价加最低价的和除以2
        data['macd_dif'], data['macd_dea'], data['macd_m'] = np.round(
            talib.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9), 2)

        data['macd_macd'] = 2 * data['macd_m']  # macd 柱状图的数值
        # 分别计算5日、10日、20日、60日的移动平均线
        ma_list = [5, 10, 20, 60]
        # 计算简单算术移动平均线MA
        for ma in ma_list:
            data['MA' + str(ma)] = np.round(talib.SMA(data['close'], ma), 2)
        # 转换Date为日期格式
        data['date'] = pd.to_datetime(data['date'])
        # 设置Date为索引
        data.set_index('date', inplace=True)
        # out_file_name = os.path.join(os.path.join(os.getcwd(), "datas/days"), "000012.csv")
        # data.to_csv(out_file_name)
        self.data = data
        return data

    def datas_week_op(self):
        pass

    def datas_month_op(self):
        pass

    def datas_season_op(self):
        pass

    def datas_year_op(self):
        pass

    def panel_init(self):
        plot_data = self.data  # 先处理好数据后才能开始进行绘画操作,这一步先初始化面板
        # print(plot_data.head())>
        # 读取显示区间最后一个交易日的数据
        last_data = plot_data.iloc[-2]
        # 设置市场线的颜色
        self.my_color = mpf.make_marketcolors(up='r',
                                              down='g',
                                              edge='inherit',
                                              wick='inherit',
                                              volume='inherit')
        # 设置图表的背景色
        self.my_style = mpf.make_mpf_style(marketcolors=self.my_color,
                                           figcolor='(0.82, 0.83, 0.85)',
                                           gridcolor='(0.82, 0.83, 0.85)')
        # 标题格式，字体为中文字体，颜色为黑色，粗体，水平中心对齐
        title_font = {'fontname': 'SimHei',
                      'size': '16',
                      'color': 'black',
                      'weight': 'bold',
                      'va': 'bottom',
                      'ha': 'center'}
        # 红色数字格式（显示开盘收盘价）粗体红色24号字
        large_red_font = {'fontname': 'Arial',
                          'size': '24',
                          'color': 'red',
                          'weight': 'bold',
                          'va': 'bottom'}
        # 绿色数字格式（显示开盘收盘价）粗体绿色24号字
        large_green_font = {'fontname': 'Arial',
                            'size': '24',
                            'color': 'green',
                            'weight': 'bold',
                            'va': 'bottom'}
        # 小数字格式（显示其他价格信息）粗体红色12号字
        small_red_font = {'fontname': 'Arial',
                          'size': '12',
                          'color': 'red',
                          'weight': 'bold',
                          'va': 'bottom'}
        # 小数字格式（显示其他价格信息）粗体绿色12号字
        small_green_font = {'fontname': 'Arial',
                            'size': '12',
                            'color': 'green',
                            'weight': 'bold',
                            'va': 'bottom'}
        # 标签格式，可以显示中文，普通黑色12号字
        normal_label_font = {'fontname': 'SimHei',
                             'size': '12',
                             'color': 'black',
                             'va': 'bottom',
                             'ha': 'right'}
        # 普通文本格式，普通黑色12号字
        normal_font = {'fontname': 'Arial',
                       'size': '12',
                       'color': 'black',
                       'va': 'bottom',
                       'ha': 'left'}
        # 使用mpf.figure()函数可以返回一个figure对象，从而进入External Axes Mode，从而实现对Axes对象和figure对象的自由控制
        fig = mpf.figure(style=self.my_style, figsize=(16, 10), facecolor=(0.82, 0.83, 0.85))
        self.ax1 = fig.add_axes([0.06, 0.25, 0.88, 0.60])
        self.ax2 = fig.add_axes([0.06, 0.15, 0.88, 0.10], sharex=self.ax1)
        self.ax3 = fig.add_axes([0.06, 0.05, 0.88, 0.10], sharex=self.ax1)
        self.ax1.set_ylabel('price')
        self.ax2.set_ylabel('volume')
        self.ax3.set_ylabel('macd')
        # 对不同的文本采用不同的格式
        t1 = fig.text(0.50, 0.94, self.title, **title_font)
        t2 = fig.text(0.12, 0.90, '开/收: ', **normal_label_font)
        t3 = fig.text(0.14, 0.89, f'{np.round(last_data["open"], 3)} / {np.round(last_data["close"], 3)}',
                      **large_red_font)
        t4 = fig.text(0.14, 0.86, f'{last_data["change"]}', **small_red_font)
        t5 = fig.text(0.22, 0.86, f'[{np.round(last_data["pct_chg"], 2)}%]', **small_red_font)
        t6 = fig.text(0.12, 0.86, f'{last_data.name.date()}', **normal_label_font)
        t7 = fig.text(0.40, 0.90, '高: ', **normal_label_font)
        t8 = fig.text(0.40, 0.90, f'{last_data["high"]}', **small_red_font)
        t9 = fig.text(0.40, 0.86, '低: ', **normal_label_font)
        t10 = fig.text(0.40, 0.86, f'{last_data["low"]}', **small_green_font)
        t11 = fig.text(0.55, 0.90, '量(万手): ', **normal_label_font)
        t12 = fig.text(0.55, 0.90, f'{np.round(last_data["volume"] / 10000, 3)}', **normal_font)
        t13 = fig.text(0.55, 0.86, '额(亿元): ', **normal_label_font)
        t14 = fig.text(0.55, 0.86, f'{last_data["amount"]}', **normal_font)
        t15 = fig.text(0.70, 0.90, '涨停: ', **normal_label_font)
        t16 = fig.text(0.70, 0.90, f'{last_data["upper_lim"]}', **small_red_font)
        t17 = fig.text(0.70, 0.86, '跌停: ', **normal_label_font)
        t18 = fig.text(0.70, 0.86, f'{last_data["lower_lim"]}', **small_green_font)
        t19 = fig.text(0.85, 0.90, '均价: ', **normal_label_font)
        t20 = fig.text(0.85, 0.90, f'{np.round(last_data["average"], 3)}', **normal_font)
        t21 = fig.text(0.85, 0.86, '昨收: ', **normal_label_font)
        t22 = fig.text(0.85, 0.86, f'{last_data["pre_close"]}', **normal_font)

    def stock_day_elements(self, timespan=120):  # 定义专属的ap元素(addplot)
        # 设置mplfinance的蜡烛颜色，up为阳线颜色，down为阴线颜色
        data = self.data.iloc[-timespan:]
        plot_data = data  # 先处理好数据后才能开始进行绘画操作
        ap = [mpf.make_addplot(plot_data[['MA5', 'MA10', 'MA20', 'MA60']], ax=self.ax1),
              mpf.make_addplot(plot_data[['macd_dif', 'macd_dea']], ax=self.ax3)]
        # 在ax3图表中绘制 MACD指标中的快线和慢线
        # 通过ax=ax1参数指定把新的线条添加到ax1中，与K线图重叠
        # 使用柱状图绘制快线和慢线的差值，根据差值的数值大小，分别用红色和绿色填充
        # 红色和绿色部分需要分别填充，因此先生成两组数据，分别包含大于零和小于等于零的数据
        bar_r = np.where(plot_data['macd_macd'] > 0, plot_data['macd_macd'], 0)
        bar_g = np.where(plot_data['macd_macd'] <= 0, plot_data['macd_macd'], 0)
        # 使用柱状图填充（type='bar')，设置颜色分别为红色和绿色
        ap.append(mpf.make_addplot(bar_r, type='bar', color='red', ax=self.ax3))
        ap.append(mpf.make_addplot(bar_g, type='bar', color='green', ax=self.ax3))
        self.ap = ap
        self.plot_data = plot_data

    def stock_week_elements(self):
        pass

    def stock_month_elements(self):
        pass

    def stock_season_elements(self):
        pass

    def stock_year_elements(self):
        pass

    def panel_draw(self):  # 表示画多少根K线
        # 调用plot()方法，注意传递addplot=ap参数，以添加均线
        mpf.plot(self.plot_data,
                 ax=self.ax1,
                 volume=self.ax2,
                 addplot=self.ap,
                 type='candle',
                 datetime_format='%Y-%m-%d',
                 style=self.my_style)
        plt.show()


# %%
if __name__ == "__main__":
    candle = stock_plot()
    candle.datas_day_op('002230.SZ.csv')
    candle.panel_init()
    candle.stock_day_elements()
    candle.panel_draw()
