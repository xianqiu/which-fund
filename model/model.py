import numpy as np
import pandas as pd

from model.df import FundTypeParamDF, FundParamDF
from fundstar.df import FundStarDF


class SimpleFundModel(object):
    
    def __init__(self, budget:int, unit:int, **kwargs):
        self.budget = budget
        self.unit = unit
        for k, v in kwargs.items():
            setattr(self, k, v)
        # 候选基金池
        self.pool = FundParamDF().df
        # 结果
        self.fund = None

    @staticmethod
    def _adjust(fractions):
        """ 已知 fractions 是一些分数，现在要把它们变成整数 integers, 满足如下条件:
        1. intergers 的和等于 fractions 的和
        2. intergers 的值尽可能接近 fractions 的值
        3. intergers 的值尽可能均匀
        """
        fractions = np.array(fractions)
        target_sum = round(fractions.sum())
        # 第一步: 向下取整
        integers = np.floor(fractions).astype(int)
        # 第二步: 计算还需要分配的差值
        remaining = target_sum - integers.sum()
        # 第三步: 计算小数部分
        decimal_parts = fractions - integers
        # 根据小数部分大小排序，取前remaining个最大的值对应的位置加1
        indices = np.argsort(decimal_parts)[::-1]
        integers[indices[:int(remaining)]] += 1
        return integers
    
    def get_type_budget(self):
        df = FundTypeParamDF().df
        # 计算被投资基金的数量
        invest_fund_num = self.budget / self.unit
        # 计算每种类型的投资数量
        invest_type_num = invest_fund_num * df.WEIGHT
        invest_type_num = invest_type_num.sort_values(ascending=False)
        df["BUDGET"] = self._adjust(invest_type_num) * self.unit
        return df[["TYPE", "BUDGET"]]

    def get_fund_by_type(self, fund_type, budget:int):
        if budget == 0:
            return None
        df = self.pool[self.pool.TYPE == fund_type]
        df = df.sort_values(by="RATE", ascending=False)
        num = int(budget / self.unit)

        if num >= len(df):
            k = num // len(df)
            s = int(num % len(df))
            fund = df[["CODE"]].reset_index()
            fund["BUDGET"] = k * self.unit
            if s > 0:
                fund.loc[0:s-1, "BUDGET"] = (k+1) * self.unit
        else:
            # 把收益率分成 num 个区间
            df["RATE_BIN"] = pd.cut(df.RATE, bins=num, include_lowest=True)
            # 计算每个区间的基金数量
            df_bin = df.groupby("RATE_BIN", observed=True).size().reset_index(name="COUNT")
            # 计算每个区间的基金数量占总数的比例
            df_bin["PROPORTION"] = df_bin.COUNT / df_bin.COUNT.sum()
            # 计算每个区间的基金数量
            weight = (df_bin.PROPORTION * num).tolist()
            df_bin["NUM"] = self._adjust(weight)

            fund_dfs = []
            # 在每一个区间，选择对应数量的基金
            for _, r in df_bin.iterrows():
                df_bin_fund = df[df.RATE_BIN == r.RATE_BIN].sort_values(by="RATE", ascending=False)
                fund_selected = df_bin_fund.iloc[:int(r.NUM)]
                # 添加到结果集合中
                fund_dfs.append(fund_selected)
            # 合并结果
            fund = pd.concat(fund_dfs).reset_index(drop=True)
            fund["BUDGET"] = self.unit

        return fund[["CODE", "BUDGET"]]

    def select(self, df:pd.DataFrame):
        df = df.sort_values(by="BUDGET", ascending=False)
        fund_dfs = []
        for _, row in df.iterrows():
            if row.BUDGET == 0:
                continue
            fund_selected = self.get_fund_by_type(row.TYPE, row.BUDGET)
            fund_dfs.append(fund_selected)
        self.fund = pd.concat(fund_dfs)


    def format(self):
        fund = self.pool.merge(self.fund, on="CODE").reset_index(drop=True)
        df = FundStarDF().df[["CODE", "NAME", "MANAGER", "COMPANY", "COUNT_5S"]]
        self.fund = fund.merge(df, on="CODE").reset_index(drop=True)

    def summarize(self):
        profit_exp = 0
        for _, row in self.fund.iterrows():
            profit_exp += row.BUDGET * row.RATE / 100
        rate_exp = profit_exp / self.budget * 100

        print(f"==== Summary ====")
        print(f"|-- 投资预算 = {self.budget} 万元")
        print(f"|-- 预期收益率 =  {rate_exp:.2f}%,  预期收益 = {profit_exp:.2f} 万元")
        print(f"|-- 基金数量 = {int(self.budget / self.unit)}")

        type_count = self.fund.groupby("TYPE").size().reset_index(name="COUNT")
        for _, row in type_count.iterrows():
            print(f"|-- [{row.TYPE}]: 数量 = {int(row.COUNT)}")

        print(f"|-- 基金列表")
        for _, row in self.fund.iterrows():
            print(f"|-- [{row.CODE:06}][{row.NAME}][{row.MANAGER}][{row.TYPE}]"
                  f"[手续费: {row.COMMISSION:.2f}%][五星评级数: {row.COUNT_5S}]")

    def run(self):
        budget = self.get_type_budget()
        self.select(budget)
        self.format()
        self.summarize()
        return self.fund
