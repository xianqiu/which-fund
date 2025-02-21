import akshare as ak

from utils.dfloader import DFLoader


class HBFundRateDF(DFLoader):

    """ 货币基金收益率
    说明：货币基金是一种投资于短期债务工具的开放式基金。
    主要投资于各种短期金融工具，如国债、央行票据、商业票据、公司债券、银行存款等。
    投资者可以随时申购和赎回货币基金，通常在 T+1 或 T+0 的时间内完成赎回。
    """
    remark = "货币基金收益率"
    header = [
        "NO",  # 序号
        "CODE",  # 基金代码
        "NAME",  # 基金简称
        "DATE",  # 日期
        "RATE_10K",  # 万份收益 (单位: %)
        "RATE_7D",  # 年化收益率7日 (单位: %)
        "RATE_14D",  # 年化收益率14日 (单位: %)
        "RATE_28D",  # 年化收益率28日 (单位: %)
        "RATE_1M",  # 近1月 (单位: %)
        "RATE_3M",  # 近3月 (单位: %)
        "RATE_6M",  # 近6月 (单位: %)
        "RATE_1Y",  # 近1年 (单位: %)
        "RATE_2Y",  # 近2年 (单位: %)
        "RATE_3Y",  # 近3年 (单位: %)
        "RATE_5Y",  # 近5年 (单位: %)
        "RATE_0Y",  # 今年来 (单位: %)
        "RATE_ALL",  # 成立来 (单位: %)
        "COMMITION",  # 手续费
    ]
    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_money_rank_em()


class CNFundRateDF(DFLoader):

    """ 场内基金收益率
    说明：
    场内基金是指在“证券交易所”上市交易的基金。
    它包括 ETF（交易所交易基金）和 LOF（上市开放式基金）。
    投资者可以像股票一样在交易所实时买卖（是投资者之间的交易，交易的标的是基金）。
    """
    remark = "场内基金收益率"
    header = [
        "NO",  # 序号
        "CODE",  # 基金代码
        "NAME",  # 基金简称
        "DATE",  # 日期
        "RATE_1",  # 单位净值
        "RATE_ACC",  # 累计净值
        "RATE_1W",  # 近1周 (单位: %)
        "RATE_1M",  # 近1月 (单位: %)
        "RATE_3M",  # 近3月 (单位: %)
        "RATE_6M",  # 近6月 (单位: %)
        "RATE_1Y",  # 近1年 (单位: %)
        "RATE_2Y",  # 近2年 (单位: %)
        "RATE_3Y",  # 近3年 (单位: %)
        "RATE_0Y",  # 今年来 (单位: %)
        "RATE_ALL",  # 成立来 (单位: %)
        "QTY",  # 可购买的量
        "COMMITION",  # 手续费
    ]
    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_exchange_rank_em()


class OpenFundRateDF(DFLoader):

    """ 开放式基金收益率
    说明：
    开放式基金是指没有固定规模，投资者可以在任何时候向“基金公司”申购或赎回的基金。
    基金的份额随投资者的申购和赎回而变化。
    """
    remark = "开放式基金收益率"
    header = [
        "NO",  # 序号
        "CODE",  # 基金代码
        "NAME",  # 基金简称
        "DATE",  # 日期
        "RATE_1",  # 单位净值
        "RATE_ACC",  # 累计净值
        "RATE_D",  # 日增长率 (单位: %)
        "RATE_1W",  # 近1周 (单位: %)
        "RATE_1M",  # 近1月 (单位: %)
        "RATE_3M",  # 近3月 (单位: %)
        "RATE_6M",  # 近6月 (单位: %)
        "RATE_1Y",  # 近1年 (单位: %)
        "RATE_2Y",  # 近2年 (单位: %)
        "RATE_3Y",  # 近3年 (单位: %)
        "RATE_0Y",  # 今年来 (单位: %)
        "RATE_ALL",  # 成立来 (单位: %)
        "CUSTOM",  # 自定义 (单位: %)
        "COMMITION",  # 手续费
    ]
    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_open_fund_rank_em(symbol="全部")


class HKFundRateDF(DFLoader):

    # 香港基金收益率
    remark = "香港基金收益率"
    header = [
        "NO",  # 序号
        "CODE",  # 基金代码
        "NAME",  # 基金简称
        "CURRENCY",  # 币种
        "DATE",  # 日期
        "RATE_1",  # 单位净值
        "RATE_D",  # 日增长率 (单位: %)
        "RATE_1W",  # 近1周 (单位: %)
        "RATE_1M",  # 近1月 (单位: %)
        "RATE_3M",  # 近3月 (单位: %)
        "RATE_6M",  # 近6月 (单位: %)
        "RATE_1Y",  # 近1年 (单位: %)
        "RATE_2Y",  # 近2年 (单位: %)
        "RATE_3Y",  # 近3年 (单位: %)
        "RATE_0Y",  # 今年来 (单位: %)
        "RATE_ALL",  # 成立来 (单位: %)
        "QTY",  # 可购买
        "HK_CODE",  # 香港基金代码
    ]
    expire = 30

    def __init__(self):
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = ak.fund_hk_rank_em()
