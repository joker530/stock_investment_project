# 这个类的名称为“RecommendIndex”
# 这个类用于定义评价策略的指标类，理论上这个类应该包含所有的评价指标，并包含所有指标的计算方法，理论上应该作为context的子属性进行使用。
# 这个类的目前需要包含的评价指标有年策略收益、年基准收益、alpha、Beta、sharpe、最大回撤,后续若需添加可以进行补充
__all__ = ["RecommendIndex"]

import numpy as np
import empyrical as em  # 直接用封装好的方法计算序列的最大回撤
import pandas as pd

import os
import sys

Base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
sys.path.append(Base_dir)

class RecommendIndex:
    def __init__(self, strategy_returns, benchmark_returns, time_span):  # 分别是回测期间产生的策略日收益率、基准日收益率（比如沪深300和标普S&P）、和回测时常
        self.strategy_returns = strategy_returns
        self.benchmark_returns = benchmark_returns
        self.time_span = time_span  # 0.5表示六个月

    def _product_of_sequence(self, seq: list):  # 用这个函数对一个序列进行加一后的累乘
        # 加上1得到新序列
        new_seq = [x + 1 for x in seq]
        # 计算新序列中所有元素的乘积
        result = np.prod(new_seq)
        return result

    def calculate_strategy_returns(self):
        # 计算策略年收益的方法
        strategy_returns_per_year = self._product_of_sequence(self.strategy_returns) / self.time_span
        return strategy_returns_per_year
        pass

    def calculate_benchmark_returns(self):
        # 计算基准收益的方法
        benchmark_returns_per_year = self._product_of_sequence(self.benchmark_returns) / self.time_span
        return benchmark_returns_per_year
        pass

    def calculate_alpha(self):
        # 计算Alpha的方法,也就是策略相较于基准的超额收益率,计算alpha有多种方法，还有拟合的方法，这只是比较基础的方法
        alpha = self.calculate_strategy_returns() - self.calculate_benchmark_returns()
        return alpha
        pass

    def calculate_beta(self):
        # 计算Beta的方法,也就是输入策略和基准的回报率序列（日回报率序列），然后计算二者序列的协方差除基准收益的方差的商
        covariance = np.cov(self.strategy_returns, self.benchmark_returns)[0, 1]
        benchmark_variance = np.var(self.benchmark_returns)
        beta = covariance / benchmark_variance
        return beta
        pass

    def calculate_sharpe_ratio(self, risk_free_rate=0.05):
        # 计算夏普比率的方法,夏普比率=（策略的年化收益率-基准无风险收益率）/年化波动率,目前的基准无风险收益率以美债为标，暂定年化5%左右
        trading_days = 252
        sharpe = ((self.calculate_strategy_returns() - risk_free_rate) /
                  np.sqrt(np.var(self.strategy_returns) * trading_days))
        return sharpe
        pass

    def calculate_max_drawdown(self):
        # 将收益率转换为累计收益率
        cumulative_returns = pd.Series(self.strategy_returns).cumsum()

        # 使用 empyrical 库计算最大回撤
        max_drawdown = em.max_drawdown(cumulative_returns)

        return max_drawdown


