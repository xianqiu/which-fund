import re

import akshare as ak

from utils.dfloader import DFLoader


class FundStarDF(DFLoader):

    """ 天天基金网-基金评级-基金评级总汇
    目标地址: https://fund.eastmoney.com/data/fundrating.html
    """
    remark = "基金评级总汇"
    header = [
        "CODE",  # 代码
        "NAME",  # 简称
        "MANAGER",  # 基金经理
        "COMPANY",  # 基金公司
        "COUNT_5S",  # 5星评级数
        "STAR_SHZQ",  # 上海证券评级
        "STAR_ZSZQ",  # 招商证券评级
        "STAR_JAJX",  # 济安金信评级
        "COMMITION",  # 手续费
        "TYPE",  # 类型
    ]
    expire = 60

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_rating_all()

