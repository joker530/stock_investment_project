# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:50:29 2023

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
# 建立爬取网站的一些基本函数，把它作为一个库进行使用
# %% 鼠标向右行走一个步长
def move_step(browser,step,t):
    action = ActionChains(browser)
    action.move_by_offset(step, 0)
    action.perform()
    time.sleep(t)
# %% 模拟鼠标悬停
def mousemove(browser,chart_element,x_pos,y_pos,t):
    action = ActionChains(browser)
    action.move_to_element(chart_element)#move_to_element_with_offset(chart_element, x_pos, y_pos)
    action.move_by_offset(x_pos, y_pos)
    #browser.maximize_window()
    action.perform()
    time.sleep(t)
# %% 定义鼠标模拟移动到元素上方,并进行点击的函数
def mouse_move_and_click(browser, element, t=0.25):
    action = ActionChains(browser)
    action.move_to_element(element)
    action.perform()
    time.sleep(t)
    element.click()
# %% 鼠标向右行走一个步长
def move_step(browser,step,t=0.1):
    action = ActionChains(browser)
    action.move_by_offset(step, 0)
    action.perform()
    time.sleep(t)
# %% 定义一个函数，用于得到想要得到的界面元素对象,可以选择获取方式
def get_element(browser, way:str, index:str):
    if way=="XPATH":
        element=browser.find_element(By.XPATH, index)
        return element
    elif way=="TAG":
        element=browser.find_element(By.TAG_NAME, index)
        return element
    elif way=="CSS":
        element=browser.find_element(By.CSS_SELECTOR, index)
        return element
    else:
        print("您输入的获取方式不对！")
# %%
def get_elements(browser, way:str, index:str):
    if way=="XPATH":
        element=browser.find_elements(By.XPATH, index)
        return element
    elif way=="TAG":
        element=browser.find_elements(By.TAG_NAME, index)
        return element
    elif way=="CSS":
        element=browser.find_elements(By.CSS_SELECTOR, index)
        return element
    else:
        print("您输入的获取方式不对！")
# %% 定义一个函数，用于获取元素中的html和里面的text文本信息
def get_ht(element):
    soup = bs(element.get_attribute('innerHTML'), 'html.parser')
    text = soup.get_text()
    return soup,text
# %% 给出tr标签中的第一个td的text内容，定位到该tr标签，且返回该tr内的所有td的text内容
def get_sibling_value(browser,text:str):
    lst=list()
    element = browser.find_element(By.XPATH , '//tr/td[contains(text(),"'+text+'")]')
    browser.execute_script("arguments[0].scrollIntoView();", element)
    next_elements=element.find_elements(By.XPATH,'following-sibling::td')
    html,text=get_ht(next_elements[0])
    for i in range(len(next_elements)):
        lst.append(next_elements[i].text)
    return lst
