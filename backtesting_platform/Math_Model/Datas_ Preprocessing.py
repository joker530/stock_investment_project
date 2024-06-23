# -*- coding: utf-8 -*-
"""
Created on Mon May  1 10:17:33 2023

@author: Administrator
"""
__all__=['remove_outliers']
# %%
import numpy as np
import pandas as pd
#import sklearn
# 这个函数用来实现中位数去极值的功能
def remove_outliers(data, coef=1.5):  #data为列向量，coef取越小所获得的数据越符合正态分布
    # 计算中位数和四分位距
    median = np.median(data)
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    
    # 计算上下截断阈值
    lower_bound = q1 - coef * iqr
    upper_bound = q3 + coef * iqr
    
    # 剔除超出截断阈值的数据点
    data_without_outliers = data[(data >= lower_bound) & (data <= upper_bound)]
    
    return data_without_outliers
# %% 这个函数用来实现行业市值对数中性化，所谓数据中性化就是消除某干扰项，如市值、财务数据对某项指标的影响
def industry_neutralize(df, industry_col, market_cap_col, return_col):
    # 按行业分类并计算市值加权平均数
    industry_mc = df.groupby(industry_col)[market_cap_col].sum()
    industry_weight = industry_mc / industry_mc.sum()

    # 计算市值占比和行业市值占比
    df['mkt_cap_weight'] = df[market_cap_col] / df[market_cap_col].sum()
    df['industry_weight'] = df[industry_col].apply(lambda x: industry_weight[x])

    # 使用线性回归拟合收益率与市值占比和行业市值占比之间的关系
    X = df[['mkt_cap_weight', 'industry_weight']]
    y = df[return_col]
    model = LinearRegression().fit(X, y)
    resid = y - model.predict(X)

    # 对残差项进行标准化处理
    zscore = (resid - resid.mean()) / resid.std()

    # 加上各自所处行业的市值加权平均数，得到中性化后的收益率
    df['neutralized_return'] = zscore + df[industry_col].apply(lambda x: industry_weight[x])

    return df
# %% 实现zscore函数
def zscore_normalize(data):   #输入的data是一个列向量
    # 计算均值和标准差
    mean = data.mean()
    std = data.std()

    # 进行标准化操作
    normalized_data = (data - mean) / std

    return normalized_data

# %%
if __name__ == "__main__":
    # 示例：使用中位数去极值处理一个随机生成的数据集
    data = np.random.normal(loc=0, scale=1, size=1000)
    data_with_outliers = np.concatenate([data, [10, -10]])  # 添加两个离群值
    data_without_outliers = remove_outliers(data_with_outliers)

    print("原始数据集大小：", len(data_with_outliers))
    print("剔除离群值后的数据集大小：", len(data_without_outliers))

