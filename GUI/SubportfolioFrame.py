# 这个文件定义了一个子账户框架以及它的启动方式
##
import time

import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
from pylab import mpl
from matplotlib.font_manager import FontProperties
from multiprocessing import Event,Queue   # 导入事件对象

# 设置显示中文字体和正负数显示
mpl.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False

##
import sys
import os

Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)

from Trade_System.Class_Base.SubPortfolio import *
from utils.date_handing import *
from Trade_System.Class_Base.Position import *

__all__ = ["SubfortfoiloFrame", "SubfortfoiloApp"]
##
class SubfortfoiloFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(SubfortfoiloFrame, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        # 第一行
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.account_name_text = wx.StaticText(panel, label="账户名称")
        hbox1.Add(self.account_name_text, flag=wx.RIGHT, border=5)
        self.account_name = wx.TextCtrl(panel, value='account1')
        hbox1.Add(self.account_name, flag=wx.RIGHT, border=5)

        self.inout_cash_text = wx.StaticText(panel, label="总出入金")
        hbox1.Add(self.inout_cash_text, flag=wx.RIGHT, border=5)
        self.inout_cash = wx.TextCtrl(panel, value='0.0')
        hbox1.Add(self.inout_cash, flag=wx.RIGHT, border=5)

        self.available_cash_text = wx.StaticText(panel, label="可用现金")
        hbox1.Add(self.available_cash_text, flag=wx.RIGHT, border=5)
        self.available_cash = wx.TextCtrl(panel, value='0.0')
        hbox1.Add(self.available_cash, flag=wx.RIGHT, border=5)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        # 第二行
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.transferable_cash_text = wx.StaticText(panel, label="可取现金")
        hbox2.Add(self.transferable_cash_text, flag=wx.RIGHT, border=5)
        self.transferable_cash = wx.TextCtrl(panel, value='0.0')
        hbox2.Add(self.transferable_cash, flag=wx.RIGHT, border=5)

        self.positions_value_text = wx.StaticText(panel, label="持仓市值")
        hbox2.Add(self.positions_value_text, flag=wx.RIGHT, border=5)
        self.positions_value = wx.TextCtrl(panel, value='0.0')
        hbox2.Add(self.positions_value, flag=wx.RIGHT, border=5)

        self.current_date_text = wx.StaticText(panel, label="当下日期")
        hbox2.Add(self.current_date_text, flag=wx.RIGHT, border=5)
        self.current_date = wx.TextCtrl(panel, value='1990-1-1')
        hbox2.Add(self.current_date, flag=wx.RIGHT, border=5)

        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        # 第三行
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.total_value_text = wx.StaticText(panel, label="账户总资")
        hbox3.Add(self.total_value_text, flag=wx.RIGHT, border=5)
        self.total_value = wx.TextCtrl(panel, value='0.0')
        hbox3.Add(self.total_value, flag=wx.RIGHT, border=5)

        self.net_value_text = wx.StaticText(panel, label="账户净资")
        hbox3.Add(self.net_value_text, flag=wx.RIGHT, border=5)
        self.net_value = wx.TextCtrl(panel, value='0.0')
        hbox3.Add(self.net_value, flag=wx.RIGHT, border=5)

        self.total_liability_text = wx.StaticText(panel, label="账户负债")
        hbox3.Add(self.total_liability_text, flag=wx.RIGHT, border=5)
        self.total_liability = wx.TextCtrl(panel, value='0.0')
        hbox3.Add(self.total_liability, flag=wx.RIGHT, border=5)

        vbox.Add(hbox3, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.text_ctr = [self.account_name, self.inout_cash, self.available_cash,
                         self.transferable_cash, self.positions_value, self.current_date,
                         self.total_value, self.net_value, self.total_liability]

        # 第四行：回测结果图表（此处使用静态文本模拟实际图表）

        # 初始化 Matplotlib 图表
        self.net_value_chart = wx.Panel(panel, size=(500, 370))
        self.net_value_chart.SetBackgroundColour(wx.Colour(240, 240, 240))
        vbox.Add(self.net_value_chart, flag=wx.EXPAND | wx.ALL, border=10)
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.font = FontProperties(family='SimHei', style='italic', weight='bold')

        # 将图像嵌入到 wx.Panel 中,这个self.canvas变成了一个控件
        self.canvas = FigureCanvas(self.net_value_chart, -1, self.fig)  # 当fig数据集变化后，用self.canvas.draw()重新绘制

        # 使用 sizer 管理布局
        chart_sizer = wx.BoxSizer(wx.VERTICAL)
        chart_sizer.Add(self.canvas, 1, wx.EXPAND)
        self.net_value_chart.SetSizer(chart_sizer)

        # 第五行，使用可滑动列表展示仓位信息
        # 创建一个滚动窗口，设置一个足够大的初始大小
        scroll_window = wx.ScrolledWindow(panel, style=wx.VSCROLL | wx.HSCROLL)
        scroll_window.SetMaxSize((570, 160))  # 设置一个最小尺寸

        self.positions_list = wx.ListCtrl(scroll_window, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.positions_list.InsertColumn(0, '代码', width=100)
        self.positions_list.InsertColumn(1, '数量', width=100)
        self.positions_list.InsertColumn(2, '价格', width=100)
        self.positions_list.InsertColumn(3, '成本', width=100)
        self.positions_list.InsertColumn(4, '持仓市值', width=100)
        self.positions_list.SetMaxSize((550, 150))

        # 将ListCtrl添加到滚动窗口中
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.positions_list, 1, wx.EXPAND | wx.ALL, 5)
        scroll_window.SetSizer(sizer)

        vbox.Add(scroll_window, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)

        # 删除按钮
        self.delete_button = wx.Button(panel, label='删除仓位')
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
        vbox.Add(self.delete_button, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)  # 一般把sizer定义好后在设置画布的展示sizer

        self.SetSize((600, 750))
        self.SetTitle('子账户显示看板')
        self.Centre()
        # 开始调用方法绘图
        self._draw_initial_plot()

    def _draw_initial_plot(self):
        x = np.linspace(-5, 5, 100)
        y = 3 * np.sin(x)

        # 更新线对象的数据
        self.line, = self.ax.plot(x, y, label="Mainline")
        self.ax.legend()
        self.ax.set_title('账户净资产走势图像', fontproperties=self.font)
        self.ax.set_xlabel('日期', fontproperties=self.font)
        self.ax.set_ylabel('金额', fontproperties=self.font)
        self.canvas.draw()  # 重新绘制图表

    def on_add(self, p: tuple):      # 每次传入一个仓位元组对象，并在仓位列表中添加一条记录
        # 添加记录的逻辑
        index = self.positions_list.InsertItem(self.positions_list.GetItemCount(), str(p[0]))
        self.positions_list.SetItem(index, 1, str(p[1]))
        self.positions_list.SetItem(index, 2, str(p[2]))
        self.positions_list.SetItem(index, 3, str(p[3]))
        self.positions_list.SetItem(index, 4, str(p[4]))

    def on_delete(self, event):
        # 删除记录的逻辑
        index = self.positions_list.GetFocusedItem()
        if index != -1:
            self.positions_list.DeleteItem(index)

    def backtest_start(self, sp: SubPortfolio, update_sp_queue: Queue, end_event: Event, start_date, end_date):  # 这个初始化后在点击开始回测时调用
        plt.ion()
        self.sp = sp

        self.ax.autoscale(enable=True, axis='y', tight=False)  # 设置y轴坐标范围为自动适应
        self.ax.set_xlim(start_date, end_date)                 # 先限制X坐标的范围
        self.canvas.draw()                                     # 更新图像

        self.dates = list()
        self.sp_net_values = list()
        self.is_plot = True
        sp_text_data_list = list()
        positions_info_list = list()
        # 考虑加锁的问题，避免出现数据混淆的情况
        while not end_event.is_set():
            if not update_sp_queue.empty():
                date, sp_text_data_list, new_sp_net_value, positions_info_list = update_sp_queue.get()
                self.dates.append(date)
                self.sp_net_values.append(new_sp_net_value)
                self.is_plot = False
            elif (len(self.dates) > 0) & (self.is_plot is False):
                wx.CallAfter(self._set_text_data, sp_text_data_list)  # 输入的参数是作为一个元组进行输入的
                wx.CallAfter(self._set_graph_data)
                wx.CallAfter(self._set_list_data, positions_info_list)
                self.is_plot = True
                time.sleep(0.5)
            else:
                pass

    def _set_text_data(self, sp_text_data_list: list):
        for i in range(len(self.text_ctr)):
            self.text_ctr[i].Clear()
            self.text_ctr[i].SetValue(str(sp_text_data_list[i]))

    def _set_graph_data(self):
        self.line.set_xdata(self.dates)  # 带self都可以理解对GUI界面的更新，需要用wx.CallAfter将其放到主线程中执行，如果更新时间过长还是会阻滞主线程
        self.line.set_ydata(self.sp_net_values)

        self.ax.relim()  # 重新计算数据范围
        self.ax.autoscale(enable=True, axis='y', tight=False)  # 只自动缩放 y 轴
        self.canvas.draw()

    def _set_list_data(self, positions_info_list: list):
        self.positions_list.DeleteAllItems()   # 调用这个方法来清空列表中的所有行
        for p in positions_info_list:
            self.on_add(p=p)
            '''在self.positions_list中添加一条记录'''

##
class SubfortfoiloApp(wx.App):
    def OnInit(self):

        self.frame = SubfortfoiloFrame(None)

        self.frame.Show(True)
        return True


if __name__ == '__main__':
    app = SubfortfoiloApp()  # 这句语句会调用OnInit方法
    app.MainLoop()
