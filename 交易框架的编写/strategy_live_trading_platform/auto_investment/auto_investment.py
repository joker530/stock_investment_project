# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 16:07:32 2023

@author: Administrator
"""

from pywinauto import Application
from time import sleep
import pywinauto.win32functions as win32func
from pywinauto import findwindows
from pywinauto.keyboard import send_keys
import win32gui
# %% 
def start_app():
    app=Application().start("G:/同花顺/同花顺安装/xiadan.exe")
# %%  用于连接同花顺专业版下单界面
def connect_window():
    app = Application(backend="uia").connect(title='专业版下单')
    main_window = app.window(title="专业版下单")
    main_window.wait('ready',timeout=10,retry_interval=1)
    return main_window
# %% 在已知控件内输入信息
def full_blank(edit, text: str):
    edit.set_focus()
    edit.type_keys(text)
# %% 清除edit控件内的内容
def chear_edit(edit, num:int):
    edit.set_focus()
    for i in range(num):
        edit.type_keys('{BACKSPACE}')
# %% 清除残余操作，保障下一次操作正常运行
def code_clear(main_win, num=6):
    edit=main_win.child_window(class_name="Edit",found_index=0)
    chear_edit(edit,num)
# %% 进行买入卖出操作
def buy_it(main):
    button=main.child_window(title="买入[B]")
    button.set_focus()  # 可以激活最小化的窗口
    button.click()
def sell_it(main):
    button=main.child_window(title="卖出[S]")
    button.set_focus()
    button.click()
# %%
def shift_bs(main_win,sb):
    children=main_win.children()
    if sb.state:
        handle=children[-2].handle
    else:
        handle=children[-1].handle
    sb.change_state()   #跳转后进行变换
    shift_bnt=main.child_window(handle=handle)
    shift_bnt.click()
# %% 计算控件之间的相对偏离位置
def get_offset(win1,handle2):
    win2=win1.child_window(handle=handle2)
    rect1=win1.rectangle()
    rect2=win2.rectangle()
    x_offset=(rect2.left+rect2.right - rect1.left - rect1.right)/2
    y_offset=(rect2.top+rect2.bottom - rect1.top - rect1.bottom)/2
    return x_offset,y_offset
# %% 点击涨停，想通过涨停价进行成交
def click_zt(main, num=11):
    children=main.children()
    zt_image=children[11]
# %% 进行买入操作,或者进行挂单
def buy_op(code:str,num:str,price:str,sb,main_win,order=True):
    if not sb.state:
       shift_bs(main_win,sb) 
    edit1 = main_win.child_window(class_name="Edit",found_index=0)
    full_blank(edit1, code)
    edit2 = main_win.child_window(class_name="Edit",found_index=2)
    full_blank(edit2, num)
    edit3 = main_win.child_window(class_name="Edit",found_index=1)  #和上面那个略有不同
    if order:
        full_blank(edit3, price)
    else:
        
    buy_it(main_win)  #点击进行购买      
# %% 进行卖出操作，或者进行挂单
def sell_op(code,num:str,price:str,sb,main_win):
    if sb.state:
        shift_bs(main_win, sb)
    edit1 = main_win.child_window(class_name="Edit",found_index=0)
    full_blank(edit1, code)
    edit2 = main_win.child_window(class_name="Edit",found_index=1)  #和上面那个略有不同
    full_blank(edit2, num)
    edit3 = main_win.child_window(class_name="Edit",found_index=2)  #和上面那个略有不同
    full_blank(edit3, price)
    sell_it(main_win)  #点击进行卖出
# %% 界面状态函数
class buy_or_sell():
    def __init__(self):
        self.state=True
    def change_state(self):
        self.state=not self.state
# %%
main = connect_window()  
code_edit = main.child_window(class_name="Edit",found_index=0)  #handle=0x000109EC
#code_edit.set_text('')
full_blank(code_edit, '601127')
# 循环按下Backspace键删除文本
chear_edit(code_edit, 6)
#full_blank(code_edit, "601127")
# %%
x_offset,y_offset=get_offset(main, code_edit, 0x00010A24)
# %%
operation_panel=main.child_window(class_name="#32770",found_index=1)
operation_panel=operation_panel.child_window(class_name="#32770",found_index=1)
button=operation_panel.child_window(class_name="Button",found_index=13)
button.click()
# %%
# 获取主窗口句柄
main_hwnd = win32gui.FindWindow(None, "专业版下单")

# 枚举主窗口下的所有子窗口
child_windows = []
win32gui.EnumChildWindows(main_hwnd, lambda hwnd, param: param.append(hwnd), child_windows)

# 打印子窗口句柄
for child_hwnd in child_windows:
    print(child_hwnd)