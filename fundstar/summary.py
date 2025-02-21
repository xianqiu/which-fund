from .df import FundStarDF


class FundStarSummary:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.source_obj = FundStarDF()
        self.df = self.source_obj.df

    def _statistics(self):
        # 基金数量
        fund_count = self.df.shape[0]
        # 计算星级的平均值（三家评级的中位数）
        df = self.df
        df["STAR_MEDIAN"] = self.df[["STAR_SHZQ", "STAR_ZSZQ", "STAR_JAJX"]].fillna(0).median(axis=1).astype(int)
        df = df.groupby(["STAR_MEDIAN"]).size().reset_index(name="COUNT")
        # 计算星级的数量
        star_count = df.set_index("STAR_MEDIAN")["COUNT"].to_dict()
        # 计算星级的百分比
        star_percent = { k: round(v / fund_count * 100, 2)
            for k, v in star_count.items() }
        # 五星基金的数量
        # k代表对应评级的机构数量，k=1,2,3,4
        star5s_fund_count = {
            k: self.df[self.df["COUNT_5S"] >= k].shape[0] for k in range(1, 5)
        }
        # 五星评级的基金经理数量
        star5s_manager_count = {
            k: self.df[self.df["COUNT_5S"] >= k]["MANAGER"].nunique() for k in range(1, 5)
        }
        # 五行基金的基金公司数量
        star5s_company_count = {
            k: self.df[self.df["COUNT_5S"] >= k]["COMPANY"].nunique() for k in range(1, 5)
        }

        return {
            "fund_count": fund_count,
            "star_count": star_count,
            "star_percent": star_percent,
            "star5s_fund_count": star5s_fund_count,
            "star5s_manager_count": star5s_manager_count,
            "star5s_company_count": star5s_company_count,
        }

    def summarize(self):
        stats = self._statistics()
        # title
        print(f"==== 数据来源: {self.source_obj.remark} "
              f"<class: {self.source_obj.__class__.__name__}> ====")
        print(f"|-- 基金数量: {stats['fund_count']}")
        print(f"|-- 基金的评级以及数量 (0代表无评级, 1-5星评级按中位数)")
        for k, v in stats["star_count"].items():
            print(f"    |-- 平均星级: {k}, 数量: {v}, 百分比: {stats['star_percent'][k]}%")
        print("|-- 五星基金数量")
        for k, v in stats["star5s_fund_count"].items():
            print(f"    |-- 五星数量: {k}, 基金数量: {v}")
        print("|-- 五星基金公司数量")
        for k, v in stats["star5s_company_count"].items():
            print(f"    |-- 五星数量: {k}, 基金公司数量: {v}")
        print("|-- 五星基金经理数量")
        for k, v in stats["star5s_manager_count"].items():
            print(f"    |-- 五星数量: {k}, 基金公司数量: {v}")
