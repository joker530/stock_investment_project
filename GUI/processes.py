import wx
import multiprocessing
import time
import random
##

##
class DataGeneratorProcess(multiprocessing.Process):
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue

    def run(self):
        while True:
            data = random.randint(0, 100)  # 模拟数据探测
            self.data_queue.put(data)  # 将数据放入队列
            time.sleep(1)


class PlottingProcess(multiprocessing.Process):
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue

    def run(self):
        app = wx.App()
        frame = MyFrame(self.data_queue)
        frame.Show()
        app.MainLoop()


class MyFrame(wx.Frame):
    def __init__(self, data_queue):
        super().__init__(None, title="Real-time Plotting", size=(400, 300))
        self.data_queue = data_queue
        self.plot_panel = wx.Panel(self)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(1000)

        self.data = None

    def on_timer(self, event):
        if not self.data_queue.empty():
            self.data = self.data_queue.get()  # 从队列中获取数据
            self.plot_panel.Refresh()  # 触发重绘

    def on_paint(self, event):
        if not self.plot_panel:
            return

        dc = wx.BufferedPaintDC(self.plot_panel)
        if self.data is not None:
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            dc.DrawLine(0, 0, self.data, self.data)