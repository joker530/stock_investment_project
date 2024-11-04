##
import datetime

import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
from pylab import mpl
from matplotlib.font_manager import FontProperties
import multiprocessing as mp  # 用这个模块处理多进程问题

import sys
import os

Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)

sys.path.append(Base_dir + '/Strategy_Functions')  # 用于导入具体策略的存放路径
from Trade_System.Class_Base.Strategy import *  # 导入策略类用于生成策略对象
import importlib
import threading  # 用这个模块创建线程
from Trade_System.Class_Base.Context import *

# from Trade_System.Class_Base.G import *  # 导入对象G

# 设置显示中文字体和正负数显示
mpl.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False

##
__all__ = ["BacktestFrame", "MyApp"]


def dynamic_import(module_name):  # 这个函数用来动态的导入模块,在使用这个函数之前请确认对应的库是否已经添加到路径
    try:
        module = importlib.import_module(name=module_name)  # 其中package是最小父文件
        return module
    except ImportError as e:
        print(f"导入模块 {module_name} 失败: {e}")
        return None


##
class BacktestFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(BacktestFrame, self).__init__(*args, **kw)

        self.context = None
        panel = wx.Panel(self)

        # 设置主垂直布局
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 第一行：编译运行 按钮 和 输入框
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.compile_button = wx.Button(panel, label="编译运行")
        hbox1.Add(self.compile_button, flag=wx.RIGHT, border=8)

        self.start_date = wx.TextCtrl(panel, value='20240101')  # 用value这个参数设置初始值
        hbox1.Add(wx.StaticText(panel, label="开始日期"), flag=wx.RIGHT, border=5)
        hbox1.Add(self.start_date, flag=wx.RIGHT, border=5)

        self.end_date = wx.TextCtrl(panel, value='20240201')
        hbox1.Add(wx.StaticText(panel, label="至"), flag=wx.RIGHT, border=5)
        hbox1.Add(self.end_date, flag=wx.RIGHT, border=5)

        self.amount = wx.TextCtrl(panel, value='100000')
        hbox1.Add(wx.StaticText(panel, label="￥"), flag=wx.RIGHT, border=5)
        hbox1.Add(self.amount, flag=wx.RIGHT, border=5)

        self.frequency = wx.ComboBox(panel, value="day", choices=["daily", "weekly", "monthly"])
        hbox1.Add(wx.StaticText(panel, label="频率"), flag=wx.RIGHT, border=5)
        hbox1.Add(self.frequency, flag=wx.RIGHT, border=5)

        self.strategy = wx.ComboBox(panel, value="SVM", choices=["海龟交易算法", "SVM", "神经网络选股"])
        hbox1.Add(wx.StaticText(panel, label="策略选择"), flag=wx.RIGHT, border=5)
        hbox1.Add(self.strategy, flag=wx.RIGHT, border=5)

        self.benchmark = wx.ComboBox(panel, value="沪深300 000300",
                                     choices=["上证指数 sh000001", "深证成指 sz399001", "创业板指 sz399006",
                                              "沪深300 sh000300"])
        hbox1.Add(wx.StaticText(panel, label="基准选择"), flag=wx.RIGHT, border=5)
        hbox1.Add(self.benchmark, flag=wx.RIGHT, border=5)

        self.start_backtest_button = wx.Button(panel, label="开始回测")
        self.start_backtest_button.Bind(wx.EVT_BUTTON, self.execute)
        hbox1.Add(self.start_backtest_button, flag=wx.RIGHT, border=8)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # 第二行：策略收益等数据
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.strategy_return = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox2.Add(wx.StaticText(panel, label="策略收益"), flag=wx.RIGHT, border=5)
        hbox2.Add(self.strategy_return, flag=wx.RIGHT, border=5)

        self.benchmark_return = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox2.Add(wx.StaticText(panel, label="基准收益"), flag=wx.RIGHT, border=5)
        hbox2.Add(self.benchmark_return, flag=wx.RIGHT, border=5)

        self.alpha = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox2.Add(wx.StaticText(panel, label="Alpha"), flag=wx.RIGHT, border=5)
        hbox2.Add(self.alpha, flag=wx.RIGHT, border=5)

        self.beta = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox2.Add(wx.StaticText(panel, label="Beta"), flag=wx.RIGHT, border=5)
        hbox2.Add(self.beta, flag=wx.RIGHT, border=5)

        self.sharpe = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox2.Add(wx.StaticText(panel, label="Sharpe"), flag=wx.RIGHT, border=5)
        hbox2.Add(self.sharpe, flag=wx.RIGHT, border=5)

        self.max_drawdown = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox2.Add(wx.StaticText(panel, label="最大回撤"), flag=wx.RIGHT, border=5)
        hbox2.Add(self.max_drawdown, flag=wx.RIGHT, border=5)

        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # 第三行：回测结果图表（此处使用静态文本模拟实际图表）

        # 初始化 Matplotlib 图表
        self.backtest_chart = wx.Panel(panel, size=(600, 400))
        self.backtest_chart.SetBackgroundColour(wx.Colour(240, 240, 240))
        vbox.Add(self.backtest_chart, flag=wx.EXPAND | wx.ALL, border=10)
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.font = FontProperties(family='SimHei', style='italic', weight='bold')

        # 将图像嵌入到 wx.Panel 中
        self.canvas = FigureCanvas(self.backtest_chart, -1, self.fig)  # 当fig数据集变化后，用self.canvas.draw()重新绘制

        # 使用 sizer 管理布局
        chart_sizer = wx.BoxSizer(wx.VERTICAL)
        chart_sizer.Add(self.canvas, 1, wx.EXPAND)
        self.backtest_chart.SetSizer(chart_sizer)

        # 第四行：日志显示和错误提示
        self.log_display = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_BESTWRAP, size=(600, 50))
        vbox.Add(self.log_display, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.error_display = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_BESTWRAP, size=(600, 50))
        vbox.Add(self.error_display, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)  # 一般把sizer定义好后在设置画布的展示sizer

        self.SetSize((1200, 700))
        self.SetTitle('量化回测平台')
        self.Centre()
        # 开始调用方法绘图
        self._draw_initial_plot()

    def _draw_initial_plot(self):
        x = np.linspace(-5, 5, 100)
        y = 3 * np.sin(x)

        # 更新线对象的数据
        self.line, = self.ax.plot(x, y)
        self.ax.set_title('更新后的函数图像')
        self.ax.set_title('回测图像', fontproperties=self.font)
        self.ax.set_xlabel('X轴', fontproperties=self.font)
        self.ax.set_ylabel('Y轴', fontproperties=self.font)
        self.canvas.draw()  # 重新绘制图表
        pass

    def on_update_data(self, update_queue, end_event):
        plt.ion()  # 打开交互模式
        returns = list()
        dates = list()
        returns_len = 0  # 初始设置收益率的长度是0
        is_plot = True  # 当这个变量为False的时候才能触发绘图
        while not end_event.is_set():
            if not update_queue.empty():
                date, rt = update_queue.get()  # 这个不是pop，队列中的元素也会被取出,对获取的二元元组进行解包处理
                dates.append(date)
                returns.append(rt)
                returns_len = len(returns)
                is_plot = False
            elif (returns_len > 0) & (is_plot == False):  # 如果收益率的长度大于0同时标记为False才绘出
                wx.CallAfter(self._update_plot, (dates, returns,))  # 输入的参数是作为一个元组进行输入的
                is_plot = True
            else:
                pass

    def _update_plot(self, dates_returns_tuple):
        dates, returns = dates_returns_tuple
        self.line.set_xdata(dates)  # 带self都可以理解对GUI界面的更新，需要用wx.CallAfter将其放到主线程中执行，如果更新时间过长还是会阻滞主线程
        self.line.set_ydata(returns)
        self.ax.relim()  # 重新计算数据范围
        self.ax.autoscale(enable=True, axis='y', tight=False)  # 只自动缩放 y 轴
        self.canvas.draw()

    def _get_dates(self):  # 得到的都是datetime.datetime对象,一般设置在点击开始回测按钮后开始触发
        # 设置日期格式
        date_format = "%Y%m%d"

        # 将格式化后的字符串设置到 TextCtrl 中
        sd = self.start_date.GetValue()
        ed = self.end_date.GetValue()

        # 将两个变量转换为datetime.datetime对象
        sd = datetime.datetime.strptime(sd, date_format)
        ed = datetime.datetime.strptime(ed, date_format)

        # 返回两个变量
        return sd, ed

    def _get_mother_money(self):  # 返回初始资金，要转化格式为float
        # 将格式化后的字符串设置到 TextCtrl 中
        money = float(self.amount.GetValue())
        return money

    def _get_frequency(self):  # 返回回测频率
        # 将格式化后的字符串设置到 TextCtrl 中
        frequency = self.frequency.GetValue()  # 以字符串的形式输出
        return frequency

    def _get_strategy(self):  # 返回回测策略对象，也就是Strategy
        # 将格式化后的字符串设置到 TextCtrl 中
        strategy_name = self.strategy.GetValue()  # 以字符串的形式输出选择的交易策略的名称
        module = dynamic_import(strategy_name)
        self.module = module
        strategy = Strategy(name=strategy_name, initialize=module.initialize, handle_data=module.handle_data,
                            before_trading_start=module.before_trading_start,
                            after_trading_end=module.after_trading_end,
                            on_strategy_end=module.on_strategy_end)
        strategy.save()  # 生成pickle文件保存一下对象，如果原文件夹本来就有这个对象就会覆盖原来的对象
        return strategy  # 返回一个Strategy对象

    def _get_benchmark(self):  # 返回选择的参考基准，类似于"沪深300 000300"
        benchmark_name = self.benchmark.GetValue()[-6:]  # 只获取后六位代码
        return benchmark_name

    def _check_process(self, strategy_process, end_event):  # 用这个函数每隔一段时间检查进程是否执行完毕
        if strategy_process.is_alive():
            wx.CallLater(100, self._check_process, strategy_process, end_event)
        else:
            end_event.set()
            # 这里还要触发回撤策略评价显示,把它放到主线程中执行
            wx.CallAfter(self._display_recommandation)   # 这个不应该放这里的
            wx.MessageBox('回测已结束', '提示', wx.OK | wx.ICON_INFORMATION)  # 弹出回测已结束的提示性窗口

    def _display_recommandation(self):  # 用这个函数触发GUI界面的评价显示
        self.strategy_return.Clear()
        strategy_return = self.context.recommand_index.calculate_strategy_returns()
        self.strategy_return.SetValue(str(strategy_return * 100) + '%')

        self.benchmark_return.Clear()
        benchmark_return = self.context.recommand_index.calculate_benchmark_returns()
        self.benchmark_return.SetValue(str(benchmark_return * 100) + '%')

        self.alpha.Clear()
        alpha = self.context.recommand_index.calculate_alpha()
        self.alpha.SetValue(str(alpha))

        self.beta.Clear()
        beta = self.context.recommand_index.calculate_beta()
        self.beta.SetValue(str(beta))

        self.sharpe.Clear()
        sharpe_ratio = self.context.recommand_index.calculate_sharpe_ratio()
        self.sharpe.SetValue(str(sharpe_ratio))

        self.max_drawdown.Clear()
        max_drowdown = self.context.recommand_index.calculate_max_drawdown()
        self.max_drawdown.SetValue(str(max_drowdown * 100) + '%')

    def execute(self, event):  # 定义当点击开始回测按钮后的 执行函数
        print('回测已启动')
        start_date, end_date = self._get_dates()  # 用自己定义的函数获得text控件里面的日期，日期为字符串

        self.ax.autoscale(enable=True, axis='y', tight=False)  # 设置y轴坐标范围为自动适应
        self.ax.set_xlim(start_date, end_date)
        self.canvas.draw()

        mother_money = self._get_mother_money()  # 格式为float
        strategy = self._get_strategy()  # 格式为Strategy对象
        frequency = self._get_frequency()  # 格式为字符串
        benchmark = self._get_benchmark()  # 格式为字符串
        context = Context(strategy=strategy, cash=mother_money, start_date=start_date, end_date=end_date,
                          freq=frequency, benchmark=benchmark)  # 此时这个上下文会自动生成一个总账户
        self.context = context
        # 从这里开始后要分成两个线程执行了，尝试用队列的方法进行两个线程中的通信，一个是主线程，一个是子线程
        update_queue = mp.Queue()  # 创建一个队列用于进程间的通信
        end_event = mp.Event()  # 创建一个事件对象
        strategy_process = mp.Process(target=context.execute_strategy, args=(update_queue,))  # 用这个创建一个新的进程
        # plot_process = mp.Process(target=self.on_update_data, args=(update_queue, end_event,))

        strategy_process.start()  # 启动这个进程
        update_date_task_thread = threading.Thread(target=self.on_update_data, args=(update_queue, end_event,))
        update_date_task_thread.start()  # 启动这个耗时的线程
        wx.CallLater(100, self._check_process, strategy_process, end_event)  # 每100毫秒检查一次进程是否结束，这个函数一般用来定期检查


##
class MyApp(wx.App):
    def OnInit(self):
        frame = BacktestFrame(None)

        frame.Show(True)
        return True


if __name__ == '__main__':
    app = MyApp()  # 这句语句会调用OnInit方法
    app.MainLoop()
