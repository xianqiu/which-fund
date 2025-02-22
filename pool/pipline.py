import pandas as pd

from fundstar.df import FundStarDF
from utils import logger


class PoolPipline:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.df = None

    def filter_status(self):
        """
        根据购买状态过滤。满足如下条件:
        1. 申购状态 = "开放申购"
        2. 赎回状态 = "开放赎回"
        3. 购买起点 <= buy_lb = 10_000
        4. 日累计限定金额 >= buy_d_ub = 100_000
        5. 手续费 <= com_lb = 0.15
        """
        buy_lb = 10_000
        buy_d_ub = 100_000
        com_lb = 0.15

        from .df import FundPurchaseDF
        df = FundPurchaseDF().df

        self.df = df[
            (df["STATUS_BUY"] == "开放申购") &
            (df["STATUS_SELL"] == "开放赎回") &
            (df["BUY_MIN"] <= buy_lb) &
            (df["BUY_MAX_D"] >= buy_d_ub) &
            (df["COMMITION"] <= com_lb)
        ]

    def filter_rate(self):
        """ 按收益率过滤。按如下方式过滤：
        1. 按3年收益率排名，取排名前 head3（单位：%）基金
        2. 按2年收益率排名，取排名前 head2（单位：%）基金
        3. 按1年收益率排名，取排名前 head1（单位：%）基金
        """
        head3 = 40
        head2 = 30
        head1 = 20

        from fundrate.df import OpenFundRateDF
        df = OpenFundRateDF().df

        # 近3年收益排序
        df3 = df[["CODE", "RATE_3Y"]].dropna(subset=["RATE_3Y"])
        df3 = df3.sort_values(by="RATE_3Y", ascending=False)
        # 取前 head3 %
        k = int((head3 / 100) * len(df3))
        df3 = df3[:k]

        # 近2年收益排序
        df2 = df[["CODE", "RATE_2Y"]].dropna(subset=["RATE_2Y"])
        df2 = df2.sort_values(by="RATE_2Y", ascending=False)
        # 取前 head2 %
        k = int((head2 / 100) * len(df2))
        df2 = df2[:k]

        # 近1年收益排序
        df1 = df[["CODE", "RATE_1Y"]].dropna(subset=["RATE_1Y"])
        df1 = df1.sort_values(by="RATE_1Y", ascending=False)
        # 取前 head1 %
        k = int((head1 / 100) * len(df1))
        df1 = df1[:k]

        # df1, d2, d3 取并集
        df = pd.concat([df1, df2, df3]).drop_duplicates()

        # self.df 与 df 取交集
        self.df = self.df[self.df.CODE.isin(df.CODE)]

    def filter_star(self):
        """按评级过滤。按如下方式过滤：
        1. 计算平均分：SATR = (TAR_SHZQ + STAR_ZSZQ + STAR_JAJX) / 3
        2. 向下取整: STAR = floor(STAR)
        2. 过滤掉平均分 STAR <= 2 的基金
        """
        from fundstar.df import FundStarDF
        df = FundStarDF().df[["CODE", "STAR_SHZQ", "STAR_ZSZQ", "STAR_JAJX"]].fillna(0)
        df["STAR"] = (df["STAR_SHZQ"] + df["STAR_ZSZQ"] + df["STAR_JAJX"]) // 3
        df = df[df.STAR > 2]
        # self.df 与 df 按 CODE 取交集
        self.df = self.df[self.df.CODE.isin(df.CODE)]

    def filter_company(self):
        """按公司过滤。按如下方式过滤：
        1. 公司的年龄 >= age_lb = 5 年
        2. 管理规模排名前 value_head (%) 的基金公司
        3. 业绩排名前 rate_head (%) 的基金公司
            业绩定义如下：公司业绩 = 公司管理的基金近3年的收益率 RATE_3Y 的中位数
        """
        age_lb = 5
        value_head = 60
        rate_head = 50

        from .df import CompanyFundValueDF
        df = CompanyFundValueDF().df

        # 1. 按年龄筛选
        # 计算公司年龄
        df['AGE'] = (pd.to_datetime('today') - pd.to_datetime(df['BUILT_DATE'], format='%Y-%m-%d')).dt.days // 365
        # 筛选年龄 >= age_lb 的行
        df = df[df.AGE >= age_lb]

        # 2. 按管理规模筛选
        # 将 UPDATE_DATE 列转换为日期格式（MM-DD）
        df['DATE'] = pd.to_datetime(df['UPDATE_DATE'], format='%m-%d')
        # 按 COMP 分组并获取最新日期对应的 FUND_VALUE
        latest_fund_value = df.sort_values('DATE').groupby('COMP').last().reset_index()
        # 筛选管理规模前 head % 的基金公司
        df = latest_fund_value[['COMP', 'FUND_VALUE']].dropna(subset=["FUND_VALUE"])
        df = df.sort_values(by="FUND_VALUE", ascending=False)
        k = int((value_head / 100) * len(df))
        comp = df[0: k].COMP

        # 3. 按业绩筛选
        from fundrate.df import OpenFundRateDF
        from fundstar.df import FundStarDF
        df = OpenFundRateDF().df
        df = df.merge(FundStarDF().df[["CODE", "COMPANY"]], on="CODE")
        df = df[df.COMPANY.isin(comp)]  # 跟前面两个条件的结果取交集
        # 计算业绩
        df = df[["CODE", "RATE_3Y", "COMPANY"]].dropna(subset=["RATE_3Y"])
        df = df.groupby("COMPANY", as_index=False).agg({"RATE_3Y": "median"})
        df = df.sort_values(by="RATE_3Y", ascending=False)
        k = int((rate_head / 100) * len(df))
        comp = df[0: k].COMPANY

        # 获取基金公司对应的基金代码
        from fundstar.df import FundStarDF
        df = FundStarDF().df
        fund = df[df.COMPANY.isin(comp)].CODE
        # 保存结果
        self.df = self.df[self.df.CODE.isin(fund)]

    def filter_manager(self):
        """按基金经理过滤。满足如下条件：
        1. 从业时间在 [exp_lb, exp_ub] 之间（单位：年）
        2. 历史最佳业绩前 rate_max_top （百分比）的基金经理
        """
        exp_lb = 5
        exp_ub = 20
        rate_max_top = 50

        from fundmgr.df import FundManagerDF
        manager = FundManagerDF().df
        # 1. 从业时间
        manager = manager[
            (manager["EXP"] >= exp_lb * 365) &
            (manager["EXP"] <= exp_ub * 365)
        ]

        # 2. 基金历史最佳业绩
        manager_by_rate = manager.groupby("NAME", as_index=False).agg({"RATE_MAX": "max"})
        manager_by_rate.sort_values(by="RATE_MAX", ascending=False)
        k = int((rate_max_top / 100) * len(manager_by_rate))
        manager_by_rate = manager_by_rate[:k]
        manager = manager[manager.NAME.isin(manager_by_rate.NAME)]
        managers_to_keep = set(manager.NAME.tolist())

        # 获取基金经理对应的基金代码
        from fundstar.df import FundStarDF
        df = FundStarDF().df
        fund_codes = []
        for _, row in df.iterrows():
            managers = row.MANAGER.strip('\"').split(',')
            if set(managers) & managers_to_keep:
                fund_codes.append(row.CODE)

        self.df = self.df[self.df.CODE.isin(fund_codes)]

    def format(self):
        """
        基金信息汇总。字段如下：
        - CODE: 基金代码
        - NAME: 基金名称
        - TYPE: 基金类型
        - COMMISSION: 手续费
        - MANAGER: 基金经理
        - COMP: 基金公司-简称
        - STAR: 综合评级（取中位数）
        - FUND_VALUE: 基金规模
        - RATE_1Y: 近1年收益率（单位：%）
        - RATE_2Y: 近2年收益率（单位：%）
        - RATE_3Y: 近3年收益率（单位：%）
        """
        self._format_by_batch()
        self._format_by_one()

    def _format_by_batch(self):
        """
        基金信息。字段如下：
        - CODE: 基金代码
        - NAME: 基金名称
        - TYPE: 基金类型
        - COMMISSION: 手续费
        - MANAGER: 基金经理
        - COMP: 基金公司-简称
        - STAR: 综合评级（取中位数）
        - FUND_VALUE: 基金规模
        - RATE_1Y: 近1年收益率（单位：%）
        - RATE_2Y: 近2年收益率（单位：%）
        - RATE_3Y: 近3年收益率（单位：%）
        """

        df = self.df[["CODE", "NAME", "TYPE", "COMMITION"]]
        from fundstar.df import FundStarDF
        df = df.merge(FundStarDF().df[["CODE", "MANAGER", "COMPANY"]], on="CODE")
        df.rename(columns={'COMPANY': 'COMP'}, inplace=True)
        star = FundStarDF().df[["STAR_SHZQ", "STAR_ZSZQ", "STAR_JAJX"]].fillna(0).median(axis=1).astype(int)
        df["STAR"] = star

        from .df import CompanyFundValueDF
        df = df.merge(CompanyFundValueDF().df[["COMP", "FUND_VALUE"]], on="COMP")

        from fundrate.df import OpenFundRateDF
        df = df.merge(OpenFundRateDF().df[["CODE", "RATE_1Y", "RATE_2Y", "RATE_3Y"]], on="CODE")

        self.df = df

    def _format_by_one(self):
        pass

    def process(self):
        # 基金筛选流程
        self.filter_status()  # 可申购的基金
        logger.info(f"[Filter]: by = '申购状态', count = {len(self.df)}")
        self.filter_rate()  # 过滤掉业绩靠后的基金
        logger.info(f"[Filter]: by = '收益率', count = {len(self.df)}")
        self.filter_star()  # 过滤掉评级低的基金
        logger.info(f"[Filter]: by = '基金评级', count = {len(self.df)}")
        self.filter_company()  # 过滤掉公司管理规模靠后的基金
        logger.info(f"[Filter]: by = '基金公司', count = {len(self.df)}")
        self.filter_manager()  # 过滤不满足条件的基金经理（基金）
        logger.info(f"[Filter]: by = '基金经理', count = {len(self.df)}")
        # 基金信息汇总
        self.format()

        return self