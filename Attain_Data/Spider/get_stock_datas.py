# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 22:54:13 2023

@author: Administrator
"""
# 这个文件用于编写可供回测和模拟交易所需要的爬虫，先编写股票的，再编写其它的
# 爬取网站雪球网。
# %%
import sys
sys.path.append('G:/ai/量化投资/交易框架的编写/spider')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re
import basic_operation_spider as bos
# %% 设置游览器
def set_browser():
    # Chrome 浏览器驱动路径
    chrome_driver_path = r"D:\ChromeDriver\chromedriver.exe"

    # Chrome 浏览器选项
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = r"C:\Users\ZhuanZ(无密码)\AppData\Local\Google\Chrome\Application\chrome.exe"
    chrome_options.add_argument("--start-maximized")

    # 启动 Chrome 浏览器驱动
    browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
    return browser
# %% 给定url和指定的游览器，在游览器内打开该页面
def to_url(browser,url,t=1):
    browser.get(url)
    time.sleep(t)
# %% 生成雪球的url
def xueqiu_url(stock_code: str):
    """
    根据股票代码生成雪球网页面链接
    :param stock_code: 股票代码，例如 '601127.SH'
    :return: 雪球网股票页面链接
    """
    prefix = "https://xueqiu.com/S/"
    suffix = stock_code.split('.')[1] + stock_code.split('.')[0]
    url = prefix + suffix
    return url
# %% 通过value值寻找第一个key
def find_key_by_value(dict_obj, value):
    for key, val in dict_obj.items():
        if val == value:
            return key
    return None
# %% 定义一个查询函数，输入一个查询的列表，可以返回一个列表中要求的所有的信息的字典
# 在已经到达该页面时可以正常运行
query=["总股本","交易性金融资产","营业收入"]
def xueqiu_stock_inquery(query: list, record:dict, code:str):
    datas=dict()
    prefix='https://xueqiu.com/snowman/S/'
    midfix=code.split('.')[1] + code.split('.')[0]
    tailfix='/detail#/'
    for i in range(len(query)):
        key=find_key_by_value(record, query[i])
        url=prefix+midfix+tailfix+key
        to_url(browser, url)
        lst=bos.get_sibling_value(browser, query[i])
        datas[query[i]]=lst
    return datas

# %% 生成一个字典，用于记录信息在哪个页面之中
query=["GSJJ","GSGG","GBJG","SDGD","LTGD","JJCG","GGZJC","GDRS","XSJJ","LHB","ZYCWZB","GSLRB","ZCFZB","XJLLB"]
def xueqiu_datas_dict(browser, query:list, code='601127.SH'):
    prefix='https://xueqiu.com/snowman/S/'
    midfix=code.split('.')[1] + code.split('.')[0]
    tailfix='/detail#/'
    record=dict()
    for i in range(len(query)):
        record[query[i]]=list()
        url=prefix+midfix+tailfix+query[i]
        to_url(browser, url)
        tbody=bos.get_elements(browser, "TAG", "tbody")
        if tbody==[]:
            tbody=bos.get_elements(browser, "XPATH", '//*[@id="app"]/div[2]/div[2]/div/table[1]')
        for j in range(len(tbody)):
            trs=bos.get_elements(tbody[j], "TAG", "tr")
            for k in range(len(trs)):
                td=bos.get_element(trs[k], "TAG", "td")
                record[query[i]].append(td.text)
    return record
record=xueqiu_datas_dict(browser, query)
##
url="https://xueqiu.com/snowman/S/SH601127/detail#/GBJG"
to_url(browser, url)
##
tbody=bos.get_element(browser, "TAG", "tbody")
trs=bos.get_elements(tbody, "TAG", "tr")
html,text=bos.get_ht(tbody)     
##
browser=set_browser()
url=xueqiu_url('601127.SH')
to_url(browser, url)
##
step=2.125   #每2.125px一分钟
start_time = time.time()
#chart_element=bos.get_element(browser, 'XPATH', '//*[@id="snbchart-status"]')
bos.mousemove(browser, chart_element, -310+30*step, 0, 0.1)
#element=bos.get_element(browser, 'XPATH', '//*[@id="overlay"]')
html,text=bos.get_ht(element)
end_time = time.time()
print("运行时间{}S".format(end_time-start_time))
# %%
# Chrome 浏览器驱动路径
chrome_driver_path = r"G:\gd\chromedriver.exe"

# Chrome 浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r"H:\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--start-maximized")

# 启动 Chrome 浏览器驱动
browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
# %%
