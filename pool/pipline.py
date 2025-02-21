import pandas as pd

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
        head3 = 20
        head2 = 25
        head1 = 30

        from fundrate.df import OpenFundRateDF
        df = OpenFundRateDF().df

        # 近3年收益排序
        df = df.sort_values(by="RATE_3Y", ascending=False)
        # 取前 head3 %
        k = int((head3 / 100) * len(df))
        df3 = df[:k]

        # 近2年收益排序
        df = df.sort_values(by="RATE_2Y", ascending=False)
        # 取前 head2 %
        k = int((head2 / 100) * len(df))
        df2 = df[:k]

        # 近1年收益排序
        df = df.sort_values(by="RATE_1Y", ascending=False)
        # 取前 head1 %
        k = int((head1 / 100) * len(df))
        df1 = df[:k]

        # df1, d2, d3 取并集
        df = pd.concat([df1, df2, df3]).drop_duplicates()

        # self.df 与 df 取交集
        self.df = self.df[self.df.CODE.isin(df.CODE)]

    def filter_star(self):
        """按评级过滤。按如下方式过滤：
        1. 过滤掉1星基金和2星基金
            判断条件：STAR_SHZQ <= 2 或 STAR_ZSZQ <= 2 或 STAR_JAJX <= 2
        """
        from fundstar.df import FundStarDF
        df = FundStarDF().df
        df = df[
            (df["STAR_SHZQ"] > 2) &
            (df["STAR_ZSZQ"] > 2) &
            (df["STAR_JAJX"] > 2)
        ]
        # self.df 与 df 取交集
        self.df = self.df[self.df.CODE.isin(df.CODE)]

    def filter_company(self):
        """按公司过滤。按如下方式过滤：
        1. 取管理规模排名前 head (%) 的基金公司
        """
        head = 50
        from .df import CompanyFundValueDF
        company = CompanyFundValueDF().df
        company = company.groupby("COMP", as_index=False).agg({"FUND_VALUE": "max"})
        company.sort_values(by="FUND_VALUE", ascending=False)
        k = int((head / 100) * len(company))
        company_to_exclude = company[k: ].COMP

        from fundstar.df import FundStarDF
        df_star = FundStarDF().df
        fund_to_exclude = df_star[df_star.COMPANY.isin(company_to_exclude)].CODE

        # 过滤掉 fund_to_exclude 中的基金
        self.df = self.df[~self.df.CODE.isin(fund_to_exclude)]

    def filter_manager(self):
        """按基金经理过滤。满足如下条件：
        1. 从业时间在 [exp_lb, exp_ub] 之间（单位：年）
        2. 基金管理规模排名前 value_top （百分比）的基金经理
        3. 历史最佳业绩前 rate_max_top （百分比）的基金经理
        """
        exp_lb = 5
        exp_ub = 20
        value_top = 60
        rate_max_top = 80

        from fundmgr.df import FundManagerDF
        manager = FundManagerDF().df
        # 从业时间
        manager = manager[
            (manager["EXP"] >= exp_lb * 365) &
            (manager["EXP"] <= exp_ub * 365)
        ]
        # 基金管理规模
        manager_by_value = manager.groupby("NAME", as_index=False).agg({"FUND_VAL": "max"})
        manager_by_value.sort_values(by="FUND_VAL", ascending=False)
        k = int((value_top / 100) * len(manager_by_value))
        manager_by_value = manager_by_value[:k]
        manager = manager[manager.NAME.isin(manager_by_value.NAME)]
        # 基金历史最佳业绩
        manager_by_rate = manager.groupby("NAME", as_index=False).agg({"RATE_MAX": "max"})
        manager_by_rate.sort_values(by="RATE_MAX", ascending=False)
        k = int((rate_max_top / 100) * len(manager_by_rate))
        manager_by_rate = manager_by_rate[:k]
        manager = manager[manager.NAME.isin(manager_by_rate.NAME)]
        managers_to_keep = set(manager.NAME.tolist())

        from fundstar.df import FundStarDF
        df = FundStarDF().df
        fund_codes = []
        for _, row in df.iterrows():
            managers = row.MANAGER.strip('\"').split(',')
            if set(managers) & managers_to_keep:
                fund_codes.append(row.CODE)

        self.df = self.df[self.df.CODE.isin(fund_codes)]

    def format_df(self):
        """
        基金信息汇总。字段如下：
        - CODE: 基金代码
        - NAME: 基金名称
        - MANAGER: 基金经理
        - COMP: 基金公司-简称
        - VALUE: 基金规模
        - TYPE: 基金类型
        - RATE_1Y: 近1年收益率（单位：%）
        - RATE_2Y: 近2年收益率（单位：%）
        - RATE_3Y: 近3年收益率（单位：%）
        - STAR: 综合评级（取中位数）
        - COMMISSION: 手续费
        """

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
        self.format_df()