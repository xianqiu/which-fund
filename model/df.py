import numpy as np

from pool import FundPoolDF
from utils import DFLoader


class FundParamDF(DFLoader):

    remark = "基金参数"
    header = [
        "CODE",  # 代码
        "TYPE",  # 简称
        "VALUE",  # 基金规模
        "RATE",  # 平均收益率
        "PROFIT",  # 平均利润
        "COMMISSION",  # 手续费(单位:%)
    ]
    expire = 0

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        df = FundPoolDF().df
        df["RATE"] = (df.RATE_1Y + df.RATE_2Y + df.RATE_3Y) / 3
        df["PROFIT"] = df.FUND_VALUE * df.RATE / 100
        df["VALUE"] = df.FUND_VALUE
        self.df = df[["CODE", "TYPE", "VALUE", "RATE", "PROFIT", "COMMISSION"]]


class FundTypeParamDF(DFLoader):

    remark = "基金类型参数"
    header = [
        "TYPE",  # 类型
        "VALUE",  # 基金规模
        "PROFIT",  # 利润
        "RATE",  # 收益率
        "WEIGHT",  # 权重
        "RATE_WEIGHT",  # 收益率权重
    ]
    expire = 0

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        df = FundParamDF().df
        # 按基金类型对 VALUE 和 PROFIT 分组求和
        df = df.groupby("TYPE").agg({'VALUE': 'sum', 'PROFIT': 'sum'}).reset_index()
        # 计算收益率
        df["RATE"] = df.PROFIT / df.VALUE
        # 计算基金类型的权重
        df["WEIGHT"] = df.VALUE / df.VALUE.sum()
        # 计算收益率权重
        # 计算 RATE * WEIGHT
        weighted_rate = df.RATE * df.WEIGHT
        # 计算 softmax
        exp_rate = np.exp(weighted_rate)
        df["RATE_WEIGHT"] = exp_rate / exp_rate.sum()
        
        self.df = df[["TYPE", "VALUE", "PROFIT", "RATE", "WEIGHT", "RATE_WEIGHT"]]
        


