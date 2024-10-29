# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:25:01 2023

@author: Administrator
"""
# 这个脚本用mplfinance实现股票的可视化操作
import pandas as pd
import mplfinance as mpf  # 注意这个库使用时，很多都是有df数据表格式输入的
import talib  # 这个库专门用于搞技术分析
import matplotlib.pyplot as plt
import numpy as np
import os

# %% mpf.plot() 函数的参数说明
'''
mpf.plot() 是一个 Python 库 mplfinance 中的函数，用于绘制金融市场股票价格走势图。下面是该函数的主要参数说明：
type：表示要绘制的价格类型，如 "candle"、"line"、"ohlc" 等。默认值为 "candle"，即绘制蜡烛图。
style：表示绘图风格，如 "charles"、"yahoo"、"yahoo"、"nightclouds" 等。可以根据自己的需求选择不同的风格，默认值为 "default"。
volume：表示是否绘制成交量，可以设置为 True 或 False。默认值为 True。
title：表示图表的标题，可以输入字符串类型的标题名称。默认值为 None。
ylabel：表示 y 轴标签名称，可以输入字符串类型的标签名称。默认值为 None。
mav：表示均线，可以输入一个整数或一组整数，代表需要显示的均线天数，如 5、10、20等。默认值为 None。
figsize：表示图表的大小，可以输入一个元组，例如 (10, 5)。默认值为 mplfinance.rcParams['figure.figsize']，即使用默认的图表大小。
savefig：表示是否保存生成的图表，可以设置为 True 或 False。默认值为 False。
show_nontrading：表示是否显示非交易日的数据，可以设置为 True 或 False。默认值为 False。
datetime_format：表示日期时间格式，可以输入字符串类型的格式代码，例如 '%Y-%m-%d'、'%Y/%m/%d %H:%M:%S' 等。默认值为 None。
xrotation：表示 x 轴的标签旋转角度，可以输入一个整数表示角度度数。默认值为 None。
tight_layouts：表示是否调整布局以适应绘图区域，可以设置为 True 或 False。默认值为 True。
以上是 mpf.plot() 函数的主要参数说明，除此之外，还有一些其他的参数可供设置，如 date_range、fill_between、lines、addplot 等，可以根据具体需要进行设置。
'''
# %% mpf.make_addplot()函数的参数说明
'''
mpf.make_addplot() 接口是 mplfinance 库中用于向绘图添加技术指标、均线、区域等信息的函数。其参数说明如下：

data: 需要添加到绘图中的数据，可以是一个 Series 或 DataFrame 对象。

type: 数据的类型，可以是 'line'（线形）或 'scatter'（散点形）。

panel: 数据所处的面板，可以是 'price'（价格面板）或 'volume'（成交量面板）。

ylabel: y 轴标签的名称，例如 'MACD'、'RSI' 等。

color: 数据在绘图中的颜色。

secondary_y: 是否将数据绘制在次级 y 轴上，通常适用于与价格关联度较低的指标。

mav: 均线的周期，可以为整数或元组/列表形式的多个周期。

width: 数据线条的宽度。

alpha: 数据线条的透明度，取值范围为 0（完全透明）到 1（不透明）。

ylim: y 轴坐标轴的范围，使用元组或列表形式表示。

ylim_lower: y 轴坐标轴的下限，可用于设置 'fill_between' 区域的下限。

ylim_upper: y 轴坐标轴的上限，可用于设置 'fill_between' 区域的上限。

fill_between: 是否在两个数据之间绘制 'fill_between' 区域。

fill_between_color: 'fill_between' 区域的颜色。


'''
# %%
# mplfinance是专门为金融数据可视化分析所提供的库
filename = "D:/量化投资/交易框架的编写/backtesting_platform/datas_daily/002230.SZ.csv"
df = pd.read_csv(filename)
df = df[['trade_date', 'open', 'close', 'high', 'low', 'vol']]
df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', ]
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
# %%
df = df[700:]
mpf.plot(df, type='candle')
# %%
mpf.plot(df, type='candle', mav=(2, 5, 10))
# %%
mpf.plot(df, type='candle', mav=(2, 5, 10), volume=True)
# %%
df['upper'], df['middle'], df['lower'] = talib.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
# print(df.tail())
add_plot = mpf.make_addplot(df[['lower']])
mpf.plot(df, addplot=add_plot, type='candle', mav=(2, 5, 10), volume=True)
# %%
b_list, s_list = data_analyze(df)
add_plot = [
    mpf.make_addplot(b_list, scatter=True, markersize=200, marker='^', color='y'),  # 设置买点的散点图
    mpf.make_addplot(s_list, scatter=True, markersize=200, marker='v', color='r'),  # 设置卖点的散点图
    mpf.make_addplot(df[['upper', 'lower']])]
mpf.plot(df, addplot=add_plot, type='candle', mav=(2, 5, 10), volume=True)
# %% 添加成交量副图
df['mavol'] = talib.MA(df['Volume'], timeperiod=10, matype=0)
b_list, s_list = data_analyze(df)
add_plot = [
    mpf.make_addplot(b_list, scatter=True, markersize=200, marker='^', color='y'),
    mpf.make_addplot(s_list, scatter=True, markersize=200, marker='v', color='r'),
    mpf.make_addplot(df[['upper', 'lower']]),
    mpf.make_addplot(df['mavol'], panel='lower', color='y', secondary_y='auto'),
]
mpf.plot(df, addplot=add_plot, type='candle', mav=(2, 5, 10), volume=True)
# %% 设置样式
"""
make_marketcolors() 设置k线颜色
up: 设置阳线柱填充颜色
down: 设置阴线柱填充颜色
edge: 设置蜡烛线边缘颜色 'i','in' 代表继承k线的颜色
wick: 设置蜡烛上下影线的颜色
volume: 设置成交量颜色
inherit: 是否继承, 如果设置了继承inherit=True，那么edge即便设了颜色也会无效
"""
my_color = mpf.make_marketcolors(up='red', down='green',
                                 edge='in', wick='in', volume='in')

# matplotlib默认不支持中文字体，设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

"""
base_mpf_style: 要继承的mplfinance风格
base_mpl_style: 要继承的matplotlib风格
marketcolors:   用于设置K线的颜色。使用mpf.make_marketcolors()方法生成。
mavcolors:  移动平均线的颜色
facecolor:  图像的填充颜色。指的是坐标系内侧的部分的颜色。
edgecolor:  坐标轴的颜色。
figcolor:   图像外周边填充色。
gridcolor:  网格线颜色。
gridstyle:  设置网格线样式，可以是’-', ‘–’, ‘-.’, ‘:’, ‘’, offset, on-off-seq
gridaxis:   网格线的方向，可以是’vertical’, ‘horizontal’, 或 ‘both’
y_on_right: 设置y轴的位置是否在右边
rc: 设置字体相关。中文和负号的正常显示问题都需要操作该参数。以字典形式传入。
legacy_rc:  也是用于设置字体格式的，不过与rc不同的是,rc仅会将rc中传入的值更新进字典，并保留原有其他字体参数。而legacy_rc会将所有原字典删除，而仅仅使用legacy_rc。
style_name: 风格名字，可以在使用mpf.write_style_file(style,filename)方法写自定义风格样式文件时使用。
"""
my_style = mpf.make_mpf_style(base_mpf_style='mike', marketcolors=my_color, gridaxis='both',
                              gridstyle='-.', y_on_right=True, rc={'font.family': 'SimHei'})

add_plot = [
    mpf.make_addplot(b_list, scatter=True, markersize=200, marker='^', color='y'),
    mpf.make_addplot(s_list, scatter=True, markersize=200, marker='v', color='r'),
    mpf.make_addplot(df[['upper', 'lower']]),
    mpf.make_addplot(df['mavol'], panel='lower', color='y', secondary_y='auto'),
]

"""
plot绘图的部分参数
type:   绘制图线的种类
ylabel: y轴标签
style:  风格样式
title:  图表标题
show_nontrading:  True 显示非交易日（k线之间有间隔）,False 不显示交易日，k线之间没有间隔
mav:    均线，格式为一个元组，如(5, 10)表示绘制5日均线和10日均线
volume: 是否绘制量柱图，默认为False，表示不绘制。
figratio:   图像横纵比，如(5,3)表示图像长比宽为5:3。
ylabel_lower:   表示底部图像的标签（一般是量柱图）
xrotation:  x轴刻度旋转度
datetime_format:    设置x轴刻度日期格式
savefig:    如果需要将图像保存为一个图片文件，则通过该参数指定文件路径即名字即可。不指定则默认不保存，但是图像会显示出来。如果指定了则图像不会直接显示出来。
"""
mpf.plot(df, type='candle', addplot=add_plot, volume=True, mav=(2, 5, 10), figscale=1.5, style=my_style, title='报价',
         figratio=(5, 5), ylabel='价格', ylabel_lower='成交量', datetime_format='%Y-%m-%d')


# %%  添加子图，格式化数据表中的信息，输出一个df表用于标准绘图
# %% 实现全功能K线图
class DataFinanceDraw(object):
    """
    获取数据，并按照 mplfinanace 需求的格式格式化，然后绘图
    """

    def __init__(self):
        self.data = pd.DataFrame()

    def my_data(self, file_name='002624.SZ.csv'):
        """
        获取数据,把数据格式化成mplfinance的标准格式
        """
        data = pd.read_csv("D:/量化投资/交易框架的编写/backtesting_platform/datas_daily/002230.SZ.csv")
        data = data[['trade_date', 'open', 'close', 'high', 'low', 'vol']]
        data.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', ]
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
        data.set_index('Date', inplace=True)
        self.data = data
        return data

    def append_macd(self):
        """
        使用talib计算macd数据
        """
        data = self.data
        data['macd_dif'], data['macd_dea'], data['macd_macd'] = talib.MACD(data['Close'], fastperiod=12,
                                                                           slowperiod=26, signalperiod=9)
        data['macd_macd'] = 2 * data['macd_macd']
        self.data = data
        return data

    def panel_draw(self):
        """
        make_addplot 绘制多个子图
        """
        data = self.data.iloc[-120:]
        # 使用柱状图绘制快线和慢线的差值，根据差值的数值大小，分别用红色和绿色填充
        # 红色和绿色部分需要分别填充，因此先生成两组数据，分别包含大于零和小于等于零的数据
        bar_r = np.where(data['macd_macd'] > 0, data['macd_macd'], 0)
        bar_g = np.where(data['macd_macd'] <= 0, data['macd_macd'], 0)
        add_plot = [
            mpf.make_addplot(data['macd_dea'], panel=2, color='b', secondary_y=False),
            mpf.make_addplot(data['macd_dif'], panel=2, color='fuchsia', secondary_y=True),
            # 使用柱状图填充（type='bar')，设置颜色分别为红色和绿色
            mpf.make_addplot(bar_r, type='bar', color='red', panel=2),
            mpf.make_addplot(bar_g, type='bar', color='green', panel=2)  # 绘制macd柱状图
        ]
        mpf.plot(data, type='candle',
                 mav=(2, 5),
                 addplot=add_plot,
                 volume=True,
                 figscale=1.5,
                 title='Candle',
                 figratio=(16, 10),
                 ylabel='price',
                 ylabel_lower='volume',
                 )

        plt.show()  # 显示
        plt.close()  # 关闭plt，释放内存


if __name__ == "__main__":
    candle = DataFinanceDraw()
    candle.my_data('002624.SZ.csv')
    candle.append_macd()
    candle.panel_draw()
'''
 mpf.plot(data, type='candle',
                 mav=(2, 5),
                 addplot=add_plot,
                 volume=True,
                 figscale=1.5,
                 title='Candle', 
                 figratio=(16, 10),
                 ylabel='price', 
                 ylabel_lower='volume',
                 main_panel=0, 
                 volume_panel=2,
                )
'''


class DataFinanceDraw(object):
    """
    获取数据，并按照 mplfinanace 需求的格式格式化，然后绘图
    """

    def __init__(self):
        self.data = pd.DataFrame()

    def my_data(self, file_name='002624.SZ.csv'):
        """
        获取数据,把数据格式化成mplfinance的标准格式
        """
        data = pd.read_csv("D:/量化投资/交易框架的编写/backtesting_platform/datas_daily/002230.SZ.csv")
        # 取需要的数据
        data = data[['trade_date', 'open', 'close', 'high', 'low', 'vol', 'amount', 'pre_close', 'change', 'pct_chg']]
        # 重命名
        data.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'pre_close', 'change', 'pct_chg']
        data['upper_lim'] = np.round(data['pre_close'] * 1.10)
        data['lower_lim'] = np.round(data['pre_close'] * 0.90)
        data['average'] = np.round((data['high'] + data['low']) / 2)
        data['macd_dif'], data['macd_dea'], data['macd_m'] = np.round(talib.MACD(data['close'], fastperiod=12,
                                                                                 slowperiod=26, signalperiod=9),
                                                                      2)
        data['macd_macd'] = 2 * data['macd_m']
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

    def panel_draw(self):
        # 设置mplfinance的蜡烛颜色，up为阳线颜色，down为阴线颜色
        my_color = mpf.make_marketcolors(up='r',
                                         down='g',
                                         edge='inherit',
                                         wick='inherit',
                                         volume='inherit')
        # 设置图表的背景色
        my_style = mpf.make_mpf_style(marketcolors=my_color,
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

        data = self.data.iloc[-120:]
        plot_data = data
        # print(plot_data.head())>
        # 读取显示区间最后一个交易日的数据
        last_data = plot_data.iloc[-2]
        # 使用mpf.figure()函数可以返回一个figure对象，从而进入External Axes Mode，从而实现对Axes对象和figure对象的自由控制
        fig = mpf.figure(style=my_style, figsize=(16, 10), facecolor=(0.82, 0.83, 0.85))
        ax1 = fig.add_axes([0.06, 0.25, 0.88, 0.60])
        ax2 = fig.add_axes([0.06, 0.15, 0.88, 0.10], sharex=ax1)
        ax3 = fig.add_axes([0.06, 0.05, 0.88, 0.10], sharex=ax1)
        ax1.set_ylabel('price')
        ax2.set_ylabel('volume')
        ax3.set_ylabel('macd')
        # 设置显示文本的时候，返回文本对象
        # 对不同的文本采用不同的格式
        t1 = fig.text(0.50, 0.94, '002624.SZ - 完美世界', **title_font)
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
        # 生成一个空列表用于存储多个addplot
        ap = [mpf.make_addplot(plot_data[['MA5', 'MA10', 'MA20', 'MA60']], ax=ax1),
              mpf.make_addplot(plot_data[['macd_dif', 'macd_dea']], ax=ax3)]
        # 在ax3图表中绘制 MACD指标中的快线和慢线
        # 通过ax=ax1参数指定把新的线条添加到ax1中，与K线图重叠
        # 使用柱状图绘制快线和慢线的差值，根据差值的数值大小，分别用红色和绿色填充
        # 红色和绿色部分需要分别填充，因此先生成两组数据，分别包含大于零和小于等于零的数据
        bar_r = np.where(plot_data['macd_macd'] > 0, plot_data['macd_macd'], 0)
        bar_g = np.where(plot_data['macd_macd'] <= 0, plot_data['macd_macd'], 0)
        # 使用柱状图填充（type='bar')，设置颜色分别为红色和绿色
        ap.append(mpf.make_addplot(bar_r, type='bar', color='red', ax=ax3))
        ap.append(mpf.make_addplot(bar_g, type='bar', color='green', ax=ax3))
        # 调用plot()方法，注意传递addplot=ap参数，以添加均线
        mpf.plot(plot_data,
                 ax=ax1,
                 volume=ax2,
                 addplot=ap,
                 type='candle',
                 datetime_format='%Y-%m-%d',
                 style=my_style)
        plt.show()


if __name__ == "__main__":
    candle = DataFinanceDraw()
    candle.my_data('002624.SZ.csv')
    candle.panel_draw()


# %% 简单的数据分析
def data_analyze(data: pd.DataFrame):
    """
    简单的数据分析，并把返回数据分析结果列表，分析的逻辑不重要，主要看如何绘制到图形中。
    """
    if data.shape[0] == 0:
        data = data
    s_list = []
    b_list = []
    b = -1
    for i, v in data['High'].iteritems():
        if v > data['upper'][i] and (b == -1 or b == 1):
            b_list.append(data['Low'][i])
            b = 0
        else:
            b_list.append(np.nan)  # 这里添加nan的目的是，对齐主图的k线数量
        if data['Low'][i] < data['lower'][i] and (b == -1 or b == 0):
            s_list.append(v)
            b = 1
        else:
            s_list.append(np.nan)
    return b_list, s_list
