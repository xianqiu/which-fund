import akshare as ak

from utils.dfloader import DFLoader


class FundManagerDF(DFLoader):

    """ 公募基金经理信息
    """
    remark = "公募基金经理信息"
    header = [
        "NO",  # 序号
        "NAME",  # 姓名
        "COMPANY",  # 所属公司
        "FUND",  # 现任基金
        "EXP",  # 累计从业天数
        "FUND_VAL",  # 现任基金资产总规模 (单位: 亿元)
        "RATE_MAX",  # 现任基金最佳回报 (单位: %)
    ]
    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_manager_em()