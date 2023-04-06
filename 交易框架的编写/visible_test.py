# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 21:30:53 2023

@author: Administrator
"""
import sys
sys.path.append('G:/ai/量化投资/交易框架的编写/trade_frame')
import trade_frame as tf
from trade_frame import pd
from trade_frame import plt
from trade_frame import dateutil
from trade_frame import matplotlib
import strategy_function_basement as sfb
# %% 产生全局实例对象,一般来说对于一个用户只调用一次即可
def generate_example():
    g=tf.G()
    trade_cal = pd.read_csv('G:\\ai\\量化投资\\trade_cal.csv')
    context=tf.Context(100000,'20220301', '20230310',trade_cal)
    return g,context,trade_cal
#g,context,trade_cal=generate_example()
# %% 初始化函数，设置基准等等
def initialize(g,context):
    # 设定002624作为基准
    tf.set_bench_mark('002624.SZ',context)
    # 5日均线全局参数
    g.ma1 = 5
    # 30日均线全局参数
    g.ma2 = 30
    # 要操作的股票601127
    g.security = '601127.SH'
    # 初始化资金量和起始日期
#initialize(g,context)
#使用vars()函数来显示对象的具体信息
#print(vars(g))
#print(vars(context))
# %% 对股票进行操作的函数，可以自己定义，每个bar（单位时间）便会调用一次
def handle_data(g,context,trade_cal):
    hist = tf.attribute_history(g.security, g.ma2, trade_cal=trade_cal, context=context)
    # 5日均线
    ma5 = hist['close'][-g.ma1:].mean()
    #print(ma5)
    # 30日均线
    ma30 = hist['close'].mean()
    #print(ma30)
    # 如果5日均线大于30日均线, 并且没有持仓, 则全仓买入
    if ma5 > ma30 and g.security not in context.positions:
        tf.order_value(g.security, context.cash, context)
    # 如果5日均线小于30日均线, 并且持仓, 则清仓
    elif ma5 < ma30 and g.security in context.positions:
        tf.order_target_value(g.security, 0 , context)
#handle_data(g,context)
# %% 框架主体函数
def run():
    # 初始化实例
    g,context,trade_cal=generate_example()
    # 创建收益数据表
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range), columns=['value'])
    # 初始资金
    initialize(g,context)
    init_value = context.cash
    last_prize = {}
    # 模拟每个bar运行
    for dt in context.date_range:
        context.dt = dateutil.parser.parse(dt)
        #print(context.dt)
        handle_data(g,context,trade_cal)
        value = context.cash
        #print(value)
        # 遍历每支股票计算股票价值
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
            #print(value)
        plt_df.loc[dt, 'value'] = value
        #print(plt_df.loc[dt, 'value'])
    # fname 为你的字体库路径和字体名
    # 图形中文显示， Matplotlib 默认情况不支持中文
    zhfont1 = matplotlib.font_manager.FontProperties(fname="G:/ai/量化投资/交易框架的编写/青鸟华光简细圆.TTF")
    # 收益率
    plt_df['ratio'] = (plt_df['value'] - init_value) / init_value
    print(plt_df['ratio'])
    bm_df = tf.attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['open'][0]
    # 基准收益率
    plt_df['benckmark_ratio'] = (bm_df['open'] - bm_init) / bm_init
    plt.title("python简单量化框架", fontproperties=zhfont1)
    # 绘制收益率曲线
    plt.plot(plt_df['ratio'], label="ratio")
    # 绘制基准收益率曲线
    plt.plot(plt_df['benckmark_ratio'], label="benckmark_ratio")
    # fontproperties 设置中文显示用字体，fontsize 设置字体大小
    plt.xlabel("日期", fontproperties=zhfont1)
    plt.ylabel("收益率", fontproperties=zhfont1)
    # x坐标斜率
    plt.xticks(rotation=46)
    # 添加图注
    plt.legend()
    # 显示
    plt.show()
run()