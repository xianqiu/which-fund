import numpy as np

from .df import FundManagerDF


class FundManagerSummary:

    def __init__(self, **kwargs):
        self.manger_top_k = 100
        self.company_top_k = 20
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.source_obj = FundManagerDF()
        self.df = self.source_obj.df

    def _statistics(self):
        # 基金经理数量, 基金公司数量
        manager_count = self.df.NO.nunique()
        company_count = self.df.COMPANY.nunique()
        # 基金经理从业年限, 中位数, 平均数, 20%分位数, 80%分位数
        manager_exp_median = self.df.EXP.median()
        manager_exp_mean = self.df.EXP.mean()
        percents = [20, 80]
        percents_to_floats = np.array(percents)/100
        manager_exp_quantile = self.df.EXP.quantile(percents_to_floats)
        # 管理基金规模, 中位数, 平均数, 20%分位数, 80%分位数
        df = self.df.groupby("NAME")["FUND_VAL"].max().reset_index()
        fund_val_median = df.FUND_VAL.median()
        fund_val_mean = df.FUND_VAL.mean()
        fund_val_quantile = df.FUND_VAL.quantile(percents_to_floats)
        # 任期最大收益率, 中位数, 平均数, 20%分位数, 80%分位数
        df = self.df.groupby(["NO", "NAME"])["RATE_MAX"].median().reset_index()
        rate_max_median = df.RATE_MAX.median()
        rate_max_mean = df.RATE_MAX.mean()
        rate_max_quantile = df.RATE_MAX.quantile(percents_to_floats)
        # top-k 基金经理: 按任期的最大收益率计算
        manager_top_k = df.sort_values("RATE_MAX", ascending=False).head(self.manger_top_k)
        # top-k 基金公司: 按最大收益率的中位数计算
        df = self.df.groupby("COMPANY")["RATE_MAX"].median().reset_index()
        company_top_k = df.sort_values("RATE_MAX", ascending=False).head(self.company_top_k)

        return {
            # 基金经理和基金公司数量
            "manager_count": manager_count,
            "company_count": company_count,
            # 基金经理从业年限
            "manager_exp_median": manager_exp_median,
            "manager_exp_mean": manager_exp_mean,
            "manager_exp_quantile": manager_exp_quantile,
            # 管理基金规模
            "fund_val_median": fund_val_median,
            "fund_val_mean": fund_val_mean,
            "fund_val_quantile": fund_val_quantile,
            # 任期最大收益率
            "rate_max_median": rate_max_median,
            "rate_max_mean": rate_max_mean,
            "percents": percents,
            "rate_max_quantile": rate_max_quantile,
            # top-k 基金经理: 按任期的最大收益率计算
            "manager_top_k": manager_top_k,
            # top-k 基金公司: 按最大收益率的中位数计算
            "company_top_k": company_top_k,
        }

    def _print_manger_top_k(self, manager):
        df = self.df[self.df.NO.isin(manager.NO)]
        df = df.groupby(['NO', 'NAME', 'COMPANY', "EXP"]).RATE_MAX.median().reset_index()
        df = df.sort_values("RATE_MAX", ascending=False)
        print(f"|-- 基金经理排行")
        for i, row in enumerate(df.itertuples(), start=1):
            print(f"   |-- {i}: {row.NAME}, {row.COMPANY}, "
                  f"从业{int(row.EXP)}天, 任期最大回报率: {row.RATE_MAX:.2f}%")

    def _print_company_top_k(self, company):
        df = self.df[self.df.COMPANY.isin(company.COMPANY)]
        df = df.groupby('COMPANY').RATE_MAX.median().reset_index()
        df = df.sort_values("RATE_MAX", ascending=False)
        print(f"|-- 基金公司排行")
        for i, row in enumerate(df.itertuples(), start=1):
            print(f"   |-- {i}: {row.COMPANY}, 基金最大回报率中位数: {row.RATE_MAX:.2f}%")

    def summarize(self):
        stats = self._statistics()
        # title
        print(f"==== 数据来源: {self.source_obj.remark} "
              f"<class: {self.source_obj.__class__.__name__}> ====")
        print(f"|-- 基金经理数量: {stats['manager_count']}, 基金公司数量: {stats['company_count']}")
        print(f"|-- 基金经理从业天数")
        print(f"   |-- 中位数 = {int(stats['manager_exp_median'])}天, "
              f"均值 = {int(stats['manager_exp_mean'])}天")
        percents = stats["percents"]
        for i, quantile in enumerate(stats['manager_exp_quantile']):
            print(f"   |-- {percents[i]}%分位数 = {quantile}天")
        print(f"|-- 基金经理任期最大收益率")
        print(f"   |-- 中位数 = {stats['rate_max_median']:.2f}%, "
              f"均值 = {stats['rate_max_mean']:.2f}%")
        for i, quantile in enumerate(stats['rate_max_quantile']):
            print(f"   |-- {percents[i]}%分位数 = {quantile:.2f}%")
        self._print_manger_top_k(stats['manager_top_k'])
        self._print_company_top_k(stats['company_top_k'])
