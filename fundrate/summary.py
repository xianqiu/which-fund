import math

import numpy as np

from .df import OpenFundRateDF, HKFundRateDF, CNFundRateDF, HBFundRateDF


class FundRateSummary:

    sources = {
        "Open": OpenFundRateDF,  # 开放基金
        "HK": HKFundRateDF,  # 香港基金
        "HB": HBFundRateDF,  # 货币基金
        "CN": CNFundRateDF,  # 场内基金
    }

    columns = {
        "6M": "RATE_6M",  # 最近六个月
        "1Y": "RATE_1Y",  # 最近一年
        "2Y": "RATE_2Y",  # 最近两年
        "3Y": "RATE_3Y",  # 最近三年
    }

    def __init__(self, source: str, span="1Y", **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        assert source in self.sources.keys(), f"source must be in {list(self.sources.keys())}"
        assert span in self.columns.keys(), f"span must be in {list(self.columns.keys())}"
        self.source=source
        self.span = span
        self.column = self.columns[span]
        self.source_obj = self.sources[source]()
        self.df = self.source_obj.df[self.column].dropna()  # 去掉空数据

    def _count_bucket(self, buckets, positive=True):
        """分桶计算区间内的基金数量（单位：%）
        :param buckets: list, 例如 [3, 5, 10, 20],
            当 positive = True 时, 代表区间 [0,3%), [3%, 5%), [5%, 10%), [10%, 20%), [20%, ∞)
        :param positive: bool, 例如 [3, 5, 10, 20],
            当positive = False 时, 代表区间 [-3%, 0), [-5%, -3%), [-10%, -5%), [-20%, -10%), (-∞, -20%)
        注意：返回结果的长度比 buckets 长度多 1
        """
        df = self.df.copy()
        if positive is False:
            df = -df[df < 0]
        buckets = [0, *buckets, math.inf]
        buckets_num = [
            len(df[(df >= buckets[i]) & (df < buckets[i + 1])])
            for i in range(len(buckets) - 1)
        ]
        return buckets_num

    def _get_percentile_ci(self, confidence_levels):
        """ 根据分位数计算置信区间
        :param confidence_levels: 置信度列表
        :return: 根据每个置信度，计算对应的置信区间。
        """
        confidence_intervals = []
        for cl in confidence_levels:
            lower_percentile = 50 - cl/2
            upper_percentile = 50 + cl/2
            lower_bound = self.df.quantile(lower_percentile / 100)
            upper_bound = self.df.quantile(upper_percentile / 100)
            confidence_intervals.append((lower_bound, upper_bound))
        return confidence_intervals

    def _statistics(self):
        # - 基金数量
        num = self.df.count()
        # - 盈利数量和占比
        profit_num = len(self.df[self.df >= 0])
        profit_ratio = profit_num / num
        # - 亏损数量和占比
        loss_num = len(self.df[self.df < 0])
        loss_ratio = loss_num / num
        # 分桶 （单位 %）
        # positive: [0, 3%), [3%, 5%), [5%, 10%), [10%, 20%), [20%, ∞)
        buckets = [3, 5, 10, 20]
        # - 桶内盈利的基金数量和占比
        buckets_profit_num = self._count_bucket(buckets, positive=True)
        buckets_profit_ratio = [
            buckets_profit_num[i] / num for i in range(len(buckets_profit_num))
        ]
        # - 桶内亏损的基金数量和占比
        buckets_loss_num = self._count_bucket(buckets, positive=False)
        buckets_loss_ratio = [
            buckets_loss_num[i] / num for i in range(len(buckets_loss_num))
        ]

        # - 收益率的中位数和均值
        rate_median = self.df.median()
        rate_mean = self.df.mean()
        # - 收益率的标准差
        rate_std = self.df.std()
        # - 百分位数 10%, 20%, 80%, 90%
        percents = [10, 20, 80, 90]
        quantiles = self.df.quantile(np.array(percents)/100)
        # - 置信区间
        confidence_levels = [95, 90, 85, 80]
        confidence_intervals = self._get_percentile_ci(confidence_levels)

        return {
            "num": num,
            "profit_num": profit_num,
            "profit_ratio": profit_ratio,
            "loss_num": loss_num,
            "loss_ratio": loss_ratio,
            "buckets": buckets,
            "buckets_profit_num": buckets_profit_num,
            "buckets_profit_ratio": buckets_profit_ratio,
            "buckets_loss_num": buckets_loss_num,
            "buckets_loss_ratio": buckets_loss_ratio,
            "rate_median": rate_median,
            "rate_mean": rate_mean,
            "rate_std": rate_std,
            "percents": percents,
            "quantiles": quantiles,
            "confidence_levels": confidence_levels,
            "confidence_intervals": confidence_intervals,
        }

    @staticmethod
    def _print_buckets(buckets, buckets_num, buckets_ratio, positive=True):
        buckets = [0, *buckets, math.inf]
        for i in range(len(buckets)-1):
            if positive:
                print(f"    |-- [{buckets[i]}%, {buckets[i+1]}%): 数量 = {buckets_num[i]}, 占比 = {buckets_ratio[i]:.2%}")
            else:
                print(f"    |-- [-{buckets[i]}%, -{buckets[i+1]}%): 数量 = {buckets_num[i]}, 占比 = {buckets_ratio[i]:.2%}")

    def summarize(self):
        stats = self._statistics()
        # title
        print(f"==== 数据来源: {self.source_obj.remark} "
              f"<source: {self.source}, span: {self.span}, class: {self.source_obj.__class__.__name__}> ====")
        print(f"|-- 基金数量: {stats['num']}")
        print(f"|-- 盈利数量: {stats['profit_num']}, 盈利占比: {stats['profit_ratio']:.2%}")
        print(f"|-- 亏损数量: {stats['loss_num']}, 亏损占比: {stats['loss_ratio']:.2%}")
        print(f"|-- 盈利的基金数量分布")
        self._print_buckets(stats["buckets"], stats["buckets_profit_num"], stats["buckets_profit_ratio"], positive=True)
        print(f"|-- 亏损的基金数量分布")
        self._print_buckets(stats["buckets"], stats["buckets_loss_num"], stats["buckets_loss_ratio"], positive=False)
        print(f"|-- 收益率")
        print(f"    |-- 中位数 = {stats['rate_median']:.2f}%, 均值 = {stats['rate_mean']:.2f}%, 标准差 = {stats['rate_std']:.2f}%")
        quantile_strings = [f"{stats['percents'][i]}% 分位数 -- {quantile:.2f}%"
                            for i, quantile in enumerate(stats['quantiles'])]
        print(f"    |-- 百分位数: {", ".join(quantile_strings)}")
        ci_strings = [f"{cl}% 置信度 -- [{ci[0]:.2f}% ~ {ci[1]:.2f}%]"
                       for cl, ci in zip(stats['confidence_levels'], stats['confidence_intervals'])]
        print(f"    |-- 置信区间: {", ".join(ci_strings)}")
