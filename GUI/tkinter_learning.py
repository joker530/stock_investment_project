# -*- coding: utf-8 -*-

import tkinter as tk

root = tk.Tk()  # 创建GUI窗口对象
# %% 添加窗口控件
label = tk.Label(root, text='Enter your name:')
label.pack()

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text='Say Hello')
button.pack()


# %% 添加事件控制函数
def on_button_clicked():
    print('Hello, %s!' % entry.get())


button.config(command=on_button_clicked)  # 将控件与回调函数关联
# %%
root.mainloop()
# %% pack布局，默认形式
root = tk.Tk()

label1 = tk.Label(root, text='Label 1', bg='red')
label1.pack()

label2 = tk.Label(root, text='Label 2', bg='green')
label2.pack()

root.mainloop()
# %% Grid布局，需要指定行和列
root = tk.Tk()

label1 = tk.Label(root, text='Label 1', bg='red')
label1.grid(row=0, column=0)

label2 = tk.Label(root, text='Label 2', bg='green')
label2.grid(row=0, column=1)

root.mainloop()
# %% Place布局，需要指定控件的坐标
root = tk.Tk()

label1 = tk.Label(root, text='Label 1', bg='red')
label1.place(x=10, y=10, width=100, height=30)

label2 = tk.Label(root, text='Label 2', bg='green')
label2.place(x=120, y=10, width=100, height=30)
root.geometry('300x200')
root.mainloop()
# %%
'''
Label控件
Label控件用于显示文本或图像等静态内容。没有回调函数。

Button控件
Button控件用于触发操作或事件。可以通过command参数设置回调函数。例如：

button = tk.Button(root, text='Click me', command=on_button_click)
Entry控件
Entry控件用于输入文本。可以通过get()方法获取文本内容。没有回调函数。

Text控件
Text控件用于显示和编辑多行文本。可以通过get()方法获取文本内容。没有回调函数。

Checkbutton控件
Checkbutton控件用于选择一个或多个选项。可以通过variable参数设置关联的变量，并在回调函数中读取变量值。例如：

var1 = tk.BooleanVar()
checkbutton1 = tk.Checkbutton(root, text='Option 1', variable=var1, command=on_checkbutton_click)
Radiobutton控件
Radiobutton控件用于从多个选项中选择一个。可以通过variable参数设置关联的变量，并在回调函数中读取变量值。例如：

var2 = tk.StringVar()
radiobutton1 = tk.Radiobutton(root, text='Option 1', variable=var2, value='option1', command=on_radiobutton_click)
radiobutton2 = tk.Radiobutton(root, text='Option 2', variable=var2, value='option2', command=on_radiobutton_click)
Scale控件
Scale控件用于选择一个数值。可以通过get()方法获取当前数值。可以通过command参数设置回调函数。例如：

scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=on_scale_change)
Listbox控件
Listbox控件用于显示和选择多个选项。可以通过get()方法获取所选选项的值。可以通过bind()方法绑定鼠标事件和回调函数。例如：

listbox = tk.Listbox(root)
listbox.bind('<<ListboxSelect>>', on_listbox_select)
Menu控件
Menu控件用于创建菜单。可以通过add_command()方法添加菜单项，并在回调函数中处理菜单项的点击事件。例如：

menu = tk.Menu(root)
menu.add_command(label='File', command=on_file_menu_click)
menu.add_command(label='Edit', command=on_edit_menu_click)

root.config(menu=menu)
以上是一些常见的Tkinter控件及其对应的回调函数。需要根据实际需求进行选择和使用。
'''
##
import wx


class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, title="创建Frame", pos=(100, 100), size=(300, 300))


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()

##
import wx


class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, title="创建StaticText类", pos=(100, 100), size=(600, 400))
        panel = wx.Panel(self)  # 创建画板
        # 创建标题，并设置字体
        title = wx.StaticText(panel, label="python", pos=(100, 20))
        font = wx.Font(16, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        title.SetFont(font)
        # 创建文本，静态的文本
        wx.StaticText(panel, label='人生苦短，我用python', pos=(50, 50))


if __name__ == '__main__':
    app = wx.App()  # 初始化应用
    frame = MyFrame(parent=None, id=-1)  # 实例化MyFrame类，并传递参数
    frame.Show()  # 显示窗口
    app.MainLoop()  # 调用主循环方法
##
import wx


class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, title="创建", size=(400, 300))
        panel = wx.Panel(self)
        self.title = wx.StaticText(panel, label="请输入用户名和密码", pos=(140, 20))
        self.label_user = wx.StaticText(panel, label="用户名", pos=(50, 50))
        self.label_pwd = wx.StaticText(panel, label="密 码", pos=(50, 90))
        self.text_user = wx.TextCtrl(panel, pos=(100, 50), size=(235, 25), style=wx.TE_LEFT)
        self.text_user = wx.TextCtrl(panel, pos=(100, 90), size=(235, 25), style=wx.TE_PASSWORD)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
##
import wx
import multiprocessing
import time
import random


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
        dc = wx.PaintDC(self.plot_panel)
        dc.Clear()
        if self.data is not None:
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            dc.DrawLine(0, 0, self.data, self.data)


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    data_generator = DataGeneratorProcess(data_queue)
    plotting_process = PlottingProcess(data_queue)

    data_generator.start()
    plotting_process.start()

    data_generator.join()
    plotting_process.join()
