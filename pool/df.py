import re

import akshare as ak

from utils.dfloader import DFLoader
from .pipline import PoolPipline


class FundPurchaseDF(DFLoader):

    """
    东方财富网站-天天基金网-基金数据-基金申购状态
    目标地址: http://fund.eastmoney.com/Fund_sgzt_bzdm.html#fcode,asc_1
    """

    remark = "基金申购状态"
    header = [
        "NO",  # 序号
        "CODE",  # 代码
        "NAME",  # 简称
        "TYPE",  # 类型
        "NAV_10K",  # 最新净值/万份收益 (NAV -- Net Asset Value)
        "NAV_10K_DATE",  # 最新净值/万份收益 报告日期
        "STATUS_BUY",  # 申购状态
        "STATUS_SELL",  # 赎回状态
        "OPEN_DATE_SELL",  # 下一个赎回开放日期
        "BUY_MIN",  # 单次申购最低金额 (单位: 元)
        "BUY_MAX_D",  # 单日累计申购最高金额 (单位: 元)
        "COMMISSION",  # 手续费 (单位: %)
    ]

    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_purchase_em()


class CompanyFundValueDF(DFLoader):
    """
        目标地址: https://fund.eastmoney.com/Company/lsgm.html
        描述: 天天基金网-基金数据-基金规模
    """

    remark = "基金公司的管理规模"
    header = [
        "NO",  # 序号
        "COMPANY",  # 基金公司
        "BUILT_DATE",  # 成立日期
        "FUND_VALUE",  # 全部管理规模
        "FUND_COUNT",  # 全部基金数量
        "MANAGER_COUNT",  # 全部经理数量
        "UPDATE_DATE",  # 更新日期
        "COMP",  # 基金公司短名称
    ]

    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_aum_em()
        self._add_comp()

    def _add_comp(self):
        # 给基金公司添加短名称
        company = self.df["基金公司"]
        suffixes = [
            "基金管理股份有限公司",
            "基金管理有限责任公司",
            "基金管理有限公司",
            "证券资产管理有限公司",
            "资产管理有限公司",
            "证券股份有限公司",
            "证券有限责任公司",
            "证券有限公司",
            "股份有限公司",
        ]

        def remove_suffix(text, suffix_list):
            # 遍历所有前缀并检查是否以该前缀结尾
            for suffix in suffix_list:
                if text.endswith(suffix):
                    # 去掉后缀并移除两端空格
                    return text[:-len(suffix)].strip()
            return text  # 如果没有匹配的后缀，则返回原文本

        short_names = []
        for name in company:
            # 如果存在括号, 则删除括号以及括号内的文本
            name = re.sub(r'\(.*?\)', '', name).strip()
            # 去掉后缀
            short_name = remove_suffix(name, suffixes)
            short_names.append(short_name)

        self.df["COMP"] = short_names


class FundPoolDF(DFLoader):

    remark = "候选基金池"
    header = None
    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = PoolPipline().process().df
