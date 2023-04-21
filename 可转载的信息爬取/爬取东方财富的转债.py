# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 18:06:14 2023

@author: Administrator
"""

import requests
from bs4 import BeautifulSoup
from msedge.selenium_tools import Edge, EdgeOptions
import cv2
import numpy as np
# %%
# 启动指定浏览器
options = webdriver.ChromeOptions()
browser = webdriver.Chrome(chrome_options=options)

# 访问目标网站
url = 'https://data.eastmoney.com/kzz/detail/113527.html'  # 这里替换成你要访问的网站
browser.get(url)
# %%
# 等待页面加载完成
browser.implicitly_wait(10)  # 等待10秒钟，直到页面加载完成

# 找到canvas元素
canvas = browser.find_element_by_css_selector('canvas[data-zr-dom-id="zr_0"]')

# 获取canvas的数据
canvas_base64 = browser.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
canvas_data = base64.b64decode(canvas_base64)

# 保存canvas数据到磁盘
with open('canvas.png', 'wb') as f:
    f.write(canvas_data)

# 关闭浏览器
browser.quit()
# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import re
# %%
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
chart_element1=browser.find_element(By.XPATH , "//*[@id='chart_1']/div[1]/canvas")
chart_element2 = browser.find_element(By.XPATH ,"//*[@id='chart_2']/div[1]/canvas")
# %%
# 定义一个函数，用于获取指定位置的走势图数据
def get_chart_data(index,graph):
    # 找到包含走势图的canvas容器
    tab_labels = browser.find_elements(By.CSS_SELECTOR, "ul li.linklab")
    if graph==1 :
        chart_xpath = "//*[@id='chart_1']/div[1]/canvas"
        tab_labels=tab_labels[0]   #点击进行切换
        chart_data = {'日期': '', '收盘价': '', '纯债价值': '', '转股价值': ''}
    elif graph==2 :
        chart_xpath = "//*[@id='chart_2']/div[1]/canvas"
        tab_labels=tab_labels[1]
        chart_data = {'日期': '', '纯债溢价率': '', '转股溢价率': ''}
    
    wait = WebDriverWait(browser, 10)    
    tab_labels.click()    #点击进行切换
    chart_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, chart_xpath)))
    # 计算鼠标悬停的位置
    width = chart_element.size['width']
    step = width // 1000
    x_pos = index * step + step // 2
    y_pos = chart_element.size['height'] // 2
    # 在走势图容器上模拟鼠标悬停，触发统计信息的显示
    # 创建一个动作链对象
    action = ActionChains(browser)
# 将鼠标移动到指定坐标，触发统计信息的显示
    action.move_to_element_with_offset(chart_element, x_pos, y_pos)

# 执行动作链中的所有动作
    browser.maximize_window()
    action.perform()
    wait.until(lambda driver: driver.execute_script('return jQuery.active == 0'))

    try:
        element2 = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='chart_1']/div[2]/table")))
    except TimeoutException:
        # 没有获取到统计信息，返回 None 
        return None

    # 解析统计信息
    for row in element2.find_elements(By.CSS_SELECTOR, "tr"):
        cells = row.find_elements(By.CSS_SELECTOR, "td")
        if len(cells) < 2:
            continue
        label_text = cells[0].text
        data_text = cells[1].text
        if '日期' in label_text:
            chart_data['日期'] = data_text
        elif '收盘价' in label_text:
            chart_data['收盘价'] = data_text
        elif graph == 1 and '纯债价值' in label_text:
            chart_data['纯债价值'] = data_text
        elif graph == 1 and '转股价值' in label_text:
            chart_data['转股价值'] = data_text
        elif graph == 2 and '纯债溢价率' in label_text:
            chart_data['纯债溢价率'] = data_text
        elif graph == 2 and '转股溢价率' in label_text:
            chart_data['转股溢价率'] = data_text

    return chart_data

    # 获取显示的统计信息
    return chart_data
# %%
# 示例：获取第10个数据点的走势图数据
data = get_chart_data(10, 1)
print(data)

#%%
# 设置Chrome浏览器driver的路径和选项
chrome_driver_path = "G:\gd\chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = "H:\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--start-maximized")

browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

# 打开目标网页
url = "https://data.eastmoney.com/kzz/detail/113527.html"
browser.get(url)
canvas_element = browser.find_element(By.XPATH, "//div[@class='chart']/div[1]/canvas")
# %%
actions = ActionChains(browser)
actions.move_to_element(canvas_element).click().perform()

# 等待页面加载完毕并获取截图
time.sleep(3)  # 等待3秒钟等待页面加载完毕
screenshot_data = browser.get_screenshot_as_png()

# 将截图数据保存为文件
with open("G:/gd/screenshot.png", "wb") as f:
    f.write(screenshot_data)

# 关闭浏览器并退出驱动程序
browser.quit()

# 查找 canvas 元素
#canvas_elements = browser.find_elements("css selector", "div.main > div.main_content > div.content > div.chart_box > div.chart > div:first-child > canvas")
#%%
# 等待页面加载完成
time.sleep(10)

# 获取canvas元素对象
canvas = driver.find_element_by_css_selector("canvas[data-zr-dom-id='zr_0']")

# 获取canvas截图
screenshot = canvas.screenshot_as_png

# 将二进制流转换为numpy数组
image_arr = np.frombuffer(screenshot, dtype=np.uint8)

# 解码为OpenCV格式图片
image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)

# 使用灰度图像进行图像处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 提取曲线信息
for c in contours:
    if len(c) > 10: # 筛选出长度大于10的轮廓（可根据实际情况调整）
        epsilon = 0.01 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(approx) > 3: # 筛选出顶点数大于3的轮廓（可根据实际情况调整）
            hull = cv2.convexHull(approx)
            area_ratio = cv2.contourArea(c) / cv2.contourArea(hull)
            if area_ratio > 0.8: # 筛选出面积比大于0.8的轮廓（可根据实际情况调整）
                polyline = approx[:,0,:]
                polynomial = np.polyfit(polyline[:,0], polyline[:,1], 3)
                x_range = np.array(range(300, 1020))
                y_range = np.polyval(polynomial, x_range)
                curve = np.column_stack((x_range, y_range))
                cv2.polylines(image, [np.int0(curve)], False, (0, 0, 255), 2)

# 保存处理后的图像
cv2.imwrite("output.jpg", image)

# 关闭游览器
driver.quit()
