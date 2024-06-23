# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 10:12:04 2023

@author: Administrator
"""
import sys

sys.path.append('D:/量化投资/交易框架的编写/backtesting_platform')
# %% 获取数据部分
from Attain_Data.Share_Info.Stock_Info_Collector import *

code = '000917.SZ'
Code = ".SZ"
sic = Stock_Info_Collector(code)
df = sic.get_Kline_datas("daily", Code=Code)
# df.to_csv('D:/量化投资/交易框架的编写/backtesting_platform/Data_Table/datas_daily/{}.csv'.format(Code))
# %% 数据可视化部分
from Visible_Functions.Visible_Stock.stock_plot import *

sp = stock_plot()
datas = sp.datas_day_op(code + Code + ".csv")
sp.panel_init()
sp.stock_day_elements(120)
sp.panel_draw()
# %% 多线程测试
import threading


def worker(num):
    """每个工作线程要执行的任务"""
    print(f"Worker {num} started")
    for i in range(10000000):
        pass
    print(f"Worker {num} finished")


# 创建5个工作线程
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))  # 设置工作目标
    threads.append(t)

# 启动所有工作线程
for t in threads:
    t.start()  # 5个线程很快就都启动了

# 等待所有工作线程完成
for t in threads:
    t.join()  # 等待它完成

print("All workers finished")
# %% 加入了锁的情况
import threading

total = 0  # 共享资源
lock = threading.Lock()  # 创建锁对象


def worker():
    """每个工作线程要执行的任务"""
    global total
    for i in range(100000):
        lock.acquire()  # 获取锁
        total += 1  # 对共享资源进行操作
        lock.release()  # 释放锁


# 创建5个工作线程
threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)

# 启动所有工作线程
for t in threads:
    t.start()

# 等待所有工作线程完成
for t in threads:
    t.join()

print(f"Total: {total}")

##
import tkinter as tk
import threading
import time
import pickle


class AccountManager:
    def __init__(self):
        self.balance = 0
        self.paused = False
        self.lock = threading.Lock()

    def start_realtime_update(self):
        # 启动一个单独的线程用于实时更新账户并渲染GUI
        t = threading.Thread(target=self.update_account)
        t.daemon = True
        t.start()

    def update_account(self):
        while True:
            with self.lock:
                if not self.paused:
                    # 模拟账户变化
                    self.balance += 1
                    # 更新GUI界面的显示
                    update_gui(self.balance)
            time.sleep(1)

    def pause_realtime_update(self):
        with self.lock:
            self.paused = True
        # 保存已计算的数据对象
        self.save_data()

    def resume_realtime_update(self):
        with self.lock:
            self.paused = False

    def save_data(self):
        with open('account_data.pkl', 'wb') as f:
            pickle.dump(self.balance, f)
        print("Data saved.")


def update_gui(balance):
    # 更新GUI界面的显示逻辑
    pass


def main():
    # 创建GUI界面
    root = tk.Tk()
    root.title("Account Real-time Update")

    account_manager = AccountManager()

    # 创建GUI元素
    label = tk.Label(root, text="Account Balance: ")
    label.pack()
    button_pause = tk.Button(root, text="Pause", command=account_manager.pause_realtime_update)
    button_pause.pack()
    button_resume = tk.Button(root, text="Resume", command=account_manager.resume_realtime_update)
    button_resume.pack()

    account_manager.start_realtime_update()

    # 运行GUI主循环
    root.mainloop()


if __name__ == "__main__":
    main()


##
def A():
    a = 1
    return a


def main(B = A):
    A = B()
    print(A)


main()
##
# 定义具体策略类
class ConcreteStrategyAdd():
    def execute(self, data):
        return sum(data)

class ConcreteStrategyMultiply():
    def execute(self, data):
        result = 1
        for num in data:
            result *= num
        return result

# 定义上下文类
class Context:
    def __init__(self, strategy):
        self._strategy = strategy

    def execute_strategy(self, data):
        return self._strategy.execute(data)

# 使用示例
data = [1, 2, 3, 4, 5]

# 使用加法策略
context = Context(ConcreteStrategyAdd())
print("Sum:", context.execute_strategy(data))

# 使用乘法策略
context = Context(ConcreteStrategyMultiply())
print("Product:", context.execute_strategy(data))
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

