# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 23:07:05 2023

@author: Administrator
"""
# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re

# Chrome 浏览器驱动路径
chrome_driver_path = r"G:\gd\chromedriver.exe"

# Chrome 浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r"H:\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--start-maximized")

# 启动 Chrome 浏览器驱动
browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

# 目标网页链接
url = "https://data.eastmoney.com/kzz/detail/113527.html"

# 打开目标网页
browser.get(url)
time.sleep(2)

# 获取走势图容器元素
#chart_element1 = browser.find_element(By.XPATH , "//*[@id='chart_1']/div[1]/canvas")
#chart_element2 = browser.find_element(By.XPATH ,"//*[@id='chart_2']/div[1]/canvas")
# %%  总函数用于输出一个pandas表存放数据
def get_pd(browser):
    #录取表一
     chart_element1 = initialize(browser, 1)
     df1 = pd.DataFrame({'日期': [], '收盘价': [], '纯债价值': [], '转股价值': []})
     step=1.0005
     date_pattern = r'\d{4}-\d{2}-\d{2}'
     price_pattern = r'-?\d+\.\d+'
     mousemove(browser,chart_element1,-450,0.25)
     for i in range(925) :
         element=browser.find_element(By.XPATH, "//*[@id='chart_1']/div[2]")
         soup = bs(element.get_attribute('innerHTML'), 'html.parser')
         div_text = soup.get_text()
         chart_data=reget(date_pattern,price_pattern,div_text,1)
         df1=df1.append(chart_data,ignore_index=True)
         move_step(browser,step,0.01)
         
     chart_element2 = initialize(browser, 2)
     df2 = pd.DataFrame({'日期': [], '转股溢价率': [], '纯债溢价率': []})
     mousemove(browser,chart_element2,-450,0.25)
     for i in range(925) :
         element=browser.find_element(By.XPATH, "//*[@id='chart_2']/div[2]")
         soup = bs(element.get_attribute('innerHTML'), 'html.parser')
         div_text = soup.get_text()
         chart_data=reget(date_pattern,price_pattern,div_text,2)
         df2=df2.append(chart_data,ignore_index=True)
         move_step(browser,step,0.01)
         
     return df1,df2

# %%合并表
def mergedf(df1,df2):
    merged_df = pd.merge(df1, df2, on='日期')
    #result_df = pd.concat([merged_df, df1.drop('日期', axis=1), df2.drop('日期', axis=1)], axis=1)
    return merged_df
#result_df.to_excel('data.xlsx')
# %%  定义一个函数，运用二分法计算每两个交易日之间的距离

def find_dpoftwo(browser , chart_element , graph , x1=-400 ,x2=-100 ,x_pre1=0,x_pre2=0):  #推荐x1=-400，x2=-100
    tol = 0.001   #两边都要满足
    mousemove(browser, chart_element, x1 , 0.25)
    if graph==1 :
        element1=browser.find_element(By.XPATH, "//*[@id='chart_1']/div[2]")
    else :
        element1=browser.find_element(By.CSS_SELECTOR , "#chart_2 > div:nth-child(2)")
    text1=bs(element1.get_attribute('innerHTML'), 'html.parser').get_text()
    print(text1)
    mousemove(browser, chart_element, x2 , 0.25)
    if graph==1 :
        element2=browser.find_element(By.XPATH, "//*[@id='chart_1']/div[2]")
    else :
        element2=browser.find_element(By.CSS_SELECTOR , "#chart_2 > div:nth-child(2)")
    text2=bs(element2.get_attribute('innerHTML'), 'html.parser').get_text()
    print(text2)
    if text1 != text2 :
        x_1 = x1
        x_2 = x1+(x2-x1)/2
        x_pre_1 = x1
        x_pre_2 = x2
        disp=find_dpoftwo(browser, chart_element, graph , x_1 , x_2 ,x_pre_1,x_pre_2)
        print(1)
    else :
        if abs(x_pre2-x2)<=tol :
            print(2)
            disp = x_pre2
        else :
            x2 = (x2 + x_pre2)/2
            print(3)
            disp=find_dpoftwo(browser, chart_element, graph , x1 ,x2,x_pre1,x_pre2 )
    return disp
# %%  计算step步长
def get_step(browser,chart_element,graph,x1=-400 ,x2=-100 ,x_pre1=0,x_pre2=0):
    disp1=find_dpoftwo(browser , chart_element , graph , x1=-400 ,x2=-100 ,x_pre1=0,x_pre2=0)
    disp2=find_dpoftwo(browser, chart_element, graph , x1=disp1 , x2=disp1+100 ,x_pre1=0,x_pre2=0)
    step=abs(disp1-disp2)
    return step
#最后获得step=1.0005051910411566,接近于1  
# %%  定义一个函数，用于获取指定位置的走势图数据
def get_chart_data(index:int, graph:int) :

    # 定位选项卡元素
    chart_element = initialize(browser, graph)
    
    # 计算鼠标悬停的位置
    width = chart_element.size['width']
    step = width // 1000
    x_pos = index * step + step // 2
    # 在走势图容器上模拟鼠标悬停，触发统计信息的显示
    mousemove(browser,chart_element, x_pos,0.25)
    #WebDriverWait(browser, 10).until(lambda driver: driver.execute_script('return jQuery.active == 0'))
    
    if graph==1 :
        element=browser.find_element(By.XPATH, "//*[@id='chart_1']/div[2]")
    else :
        element=browser.find_element(By.CSS_SELECTOR , "#chart_2 > div:nth-child(2)")
    soup = bs(element.get_attribute('innerHTML'), 'html.parser')
    print(soup)
    div_text = soup.get_text()
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    price_pattern = r'-?\d+\.\d+'
    
    chart_data=reget(date_pattern,price_pattern,div_text,graph)

    return chart_data
# %% 定位选项卡元素和界面初始化
def initialize(browser,graph):
    tab_labels = browser.find_elements(By.CSS_SELECTOR, "ul li.linklab")
    if graph == 1:
        chart_xpath = "//*[@id='chart_1']/div[1]/canvas"
        tab_labels[0].click()
    else :
        chart_xpath = "//*[@id='chart_2']/div[1]/canvas"
        tab_labels[1].click()
    # 切换至目标走势图
        
    chart_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, chart_xpath)))
    return chart_element
# %% 鼠标向右行走一个步长
def move_step(browser,step,t):
    action = ActionChains(browser)
    action.move_by_offset(step, 0)
    action.perform()
    time.sleep(t)
# %% 模拟鼠标悬停
def mousemove(browser,chart_element,x_pos,t):
    action = ActionChains(browser)
    action.move_to_element(chart_element)#move_to_element_with_offset(chart_element, x_pos, y_pos)
    action.move_by_offset(x_pos, 0)
    #browser.maximize_window()
    action.perform()
    time.sleep(t)
    print(x_pos)
# %% 用re获得各种信息包含在chart_data中
def reget(date_pattern,price_pattern,div_text,graph):
    #print(div_text)
    if graph == 1 :
        date = re.search(date_pattern, div_text).group(0)
        try :
            closing_price = (re.search( r'收盘价:'+ price_pattern, div_text).group(0))
            closing_price = float(re.search(price_pattern , closing_price).group(0))
        except :
            closing_price = 0
        pure_bond_value = (re.search( r'纯债价值:'+ price_pattern, div_text).group(0))
        pure_bond_value = float(re.search(price_pattern , pure_bond_value).group(0))
        convertible_bond_value = (re.search( r'转股价值:'+ price_pattern, div_text).group(0))
        convertible_bond_value = float(re.search(price_pattern , convertible_bond_value).group(0))
        chart_data = {'日期': date, '收盘价': closing_price, '纯债价值': pure_bond_value, '转股价值': convertible_bond_value}
    else :
        date = re.search(date_pattern, div_text).group(0)
        ex_stock = (re.search( r'转股溢价率:'+ price_pattern, div_text).group(0))
        ex_stock = float((re.search( price_pattern, ex_stock).group(0)))/100
        ex_debt = (re.search( r'纯债溢价率:'+ price_pattern , div_text).group(0))
        ex_debt = float((re.search( price_pattern, ex_debt).group(0)))/100
        chart_data = {'日期': date, '转股溢价率': ex_stock , '纯债溢价率': ex_debt }
    return chart_data

