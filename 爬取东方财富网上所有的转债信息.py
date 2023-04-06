# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 13:28:34 2023

@author: Administrator
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re
# %% 打开东方财富网的可转载页面
# Chrome 浏览器驱动路径
chrome_driver_path = r"G:\gd\chromedriver.exe"

# Chrome 浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r"H:\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--start-maximized")

# 启动 Chrome 浏览器驱动
browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

# 目标网页链接
url = "https://data.eastmoney.com/xg/xg/?mkt=kzz"

# 打开目标网页
browser.get(url)
time.sleep(0.2)
#browser.execute_script('window.open("https://data.eastmoney.com/kzz/detail/123187.html");')
#time.sleep(3)  # 等待加载完成
# %%
# 切换到第二个页面并关闭
#handles = browser.window_handles
#browser.switch_to.window(handles[1])
#browser.close()

# 切换回第一个页面
#browser.switch_to.window(handles[0])

# 关闭浏览器
#browser.quit()
# %%  构建主函数，用来爬取目前未退市且已上市的所有转债的基础信息
def get_all_data(browser,df1=pd.DataFrame(),df2=pd.DataFrame()):
    num_tr=get_tr_num(browser)
    print(num_tr)
    for i in range(num_tr):
        tr_temp=get_tr(browser, i+1)
        print(is_td_link(tr_temp, i+1))
        if is_td_link(tr_temp, i+1):  #如果td[2]有链接
            td_code,data_temp=get_data(tr_temp)    #获取主页面中的数据
            print(data_temp)
            df1=df1.append(data_temp,ignore_index=True)
            link_temp=combine_link(td_code)
            #print(link_temp)
            open_page(browser, link_temp)
            time.sleep(2.5)    #驻留2.5秒
            text=find_in_detail(browser)   #获取detail页中想要的的数据
            print(text)
            df2=df2.append(text,ignore_index=True)
            close_page(browser,1)        #关闭第二个page
    browser.get("https://data.eastmoney.com/xg/xg/?mkt=kzz")
    try:
        next_page()
        get_all_data(browser,df1=df1,df2=df2)    #进行遍历
    except:
        return df1,df2
        print("函数执行完成")  
# %%  判断获取元素中是否有链接
#element1=browser.find_element(By.XPATH,'//*[@id="dataview_kzz"]/div[2]/div[2]/table/tbody/tr[18]/td[2]')
def is_link(element):
    html = element.get_attribute('innerHTML')
    if 'href' in html:
        return True
    else:
        return False
# %%  从tr元素中提取td[2]元素，并判断是否有链接
def is_td_link(tr_element,num_tr):
    td2=tr_element.find_element(By.XPATH,"//tr["+str(num_tr)+"]/td[2]")
    return is_link(td2)
# %%  获取转债数字代码和名称
#element1=browser.find_element(By.XPATH,'//*[@id="dataview_kzz"]/div[2]/div[2]/table/tbody/tr[18]/td[2]')
def get_code(element1,element2):
    return element1.text,element2.text
# %%  打开给定链接的页面,并等待t秒加载,加载后进行设置link为当前url
def open_page(browser,link):
    script = 'window.open("{}");'.format(link)
    browser.execute_script(script)
    handles = browser.window_handles
    browser.switch_to.window(handles[1])
# %%  切换页面,并关闭
def close_page(browser,num):  
    handles = browser.window_handles  #定义句柄对象
    browser.close()
    browser.switch_to.window(handles[num-1])
# %%  组合链接函数
def combine_link(code):
    link = "https://data.eastmoney.com/kzz/detail/"+code+".html"
    return link
# %%  定义鼠标模拟移动到元素上方,并进行点击的函数
def mouse_move_and_click(browser, element, t=0.25):
    action = ActionChains(browser)
    action.move_to_element(element)
    action.perform()
    time.sleep(t)
    element.click()
# %%  定义一个函数，用于跳转到tr中的详细对应的页面
def To_detail_page(tr_element,browser=browser):
    td=tr_element.find_elements(By.TAG_NAME, "td")
    td1=td[0]
    link=combine_link(td1.text)
    open_page(browser, link)
# %%  定义一个函数，用于模拟鼠标点击下一页
def next_page(browser=browser,t=0.5):
    handles = browser.window_handles
    browser.switch_to.window(handles[-1])
    time.sleep(1)
    element = browser.find_element(By.XPATH, '//a[contains(text(), "下一页")]')
    mouse_move_and_click(browser, element, t)
# %% 获取当前一个界面中<tbody>中<tr>标签中的数量
def get_tr_num(browser):
    tbody_tag = browser.find_element(By.TAG_NAME, 'tbody')
    num_tr = len(tbody_tag.find_elements(By.TAG_NAME, 'tr'))
    return num_tr
# %% 给定一个序列号返回所对应的tr元素
def get_tr(browser,num_tr):
    tbody_tag=browser.find_element(By.TAG_NAME, 'tbody')
    #print(tbody_tag.text)
    target="//tr["+str(num_tr)+"]"
    tr_element=tbody_tag.find_element(By.XPATH, target)
    return tr_element
# %% 获取tr标签中所有的必要信息并返还给data_plice
def get_data(element):
    price_pattern = r'-?\d+\.\d+'
    td=element.find_elements(By.TAG_NAME, 'td')
    td_code=td[0].text
    td_name=td[1].text
    td_stock_price=float(td[8].text)
    td_tstock_price=float(td[9].text)
    td_tvalue=float(td[10].text)
    td_ex_stock_rate=float(re.search(price_pattern, td[12].text).group(0))/100
    td_credit_recommendation=td[19].text
    data_plice={"债券代码":td_code,"债券简称":td_name,"正股价":td_stock_price,"转股价":td_tstock_price,"转股价值":td_tvalue,"转股溢价率":td_ex_stock_rate,"信用评级":td_credit_recommendation}
    return td_code,data_plice
element=get_tr(browser, 7)
data=get_data(element)
# %% 获取在详细页面中的一些必要信息
def find_in_detail(browser):
    text={'正股市净率':'','回售触发价':'','强赎触发价':''}
    for key in text.keys():
        element = browser.find_element(By.XPATH , '//tr/td[contains(text(),"'+key+'")]')
        browser.execute_script("arguments[0].scrollIntoView();", element)
        try:
            next_element=element.find_element(By.XPATH,'following-sibling::td')
            text[key]=next_element.text
        except NoSuchElementException:
            print('未找到目标元素的兄弟节点')
    return text
# %%


