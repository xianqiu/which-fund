import akshare as ak
import pandas as pd

from utils import DFLoader, logger, WT


class FundRiskDF(DFLoader):

    """
    描述: 雪球基金-基金详情-数据分析
    目标地址: https://danjuanfunds.com/funding/000001
    """

    remark = "基金风险分析"
    header = [
        "CODE",  # 基金代码
        "PERIOD",  # 周期
        "RISK_REWARD",  # 风险与收益的比值
        "VOLATILITY",  # 波动率
        "SHARPE_RATIO",  # 夏普比率,
        "MAX_DRAW_DOWN",  # 最大回撤
    ]
    expire = 30

    def __init__(self, codes):
        self.codes = codes
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = pd.DataFrame()
        for code in self.codes:
            try:
                WT.wait()
                df = ak.fund_individual_analysis_xq(symbol=code)
                df["CODE"] = code
                df = df[self.header]
                self.df.append(df)
                status = "SUCCESS"
                msg = None
            except Exception as e:
                msg = e
                status = "FAIL"
            logger.info(f"[Get]: code = {code}, status = {status}, message = {msg}")


class FundProfitDF(DFLoader):

    """
    目标地址: https://danjuanfunds.com/funding/000001
    描述: 雪球基金-基金详情-盈利概率；历史任意时点买入，持有满X时间，盈利概率，以及平均收益
    """

    remark = "基金盈利概率分析"
    header = [
        "CODE",  # 基金代码
        "TIMESPAN",  # 持有时长
        "PROFIT_PROB",  # 盈利概率
        "PROFIT_EXPECTED",  # 平均收益
    ]
    expire = 30

    def __init__(self, codes):
        self.codes = codes
        super().__init__(expire=self.expire,
                         header=self.header)

    def get(self):
        self.df = pd.DataFrame()
        for code in self.codes:
            try:
                WT.wait()
                df = ak.fund_individual_profit_probability_xq(symbol=code)
                df["CODE"] = code
                df = df[self.header]
                self.df.append(df)
                status = "SUCCESS"
                msg = None
            except Exception as e:
                msg = e
                status = "FAIL"
            logger.info(f"[Get]: code = {code}, status = {status}, message = {msg}")
