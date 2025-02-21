class RunFundRate:

    @staticmethod
    def plot():
        from fundrate import FundRatePlot
        # 基金收益的分布图
        FundRatePlot("Open", "1Y").hist()

    @staticmethod
    def summarize():
        from fundrate import FundRateSummary
        # source: Open - 开放式基金, HK - 香港基金, HB - 货币基金, CN - 场内基金
        # span: 6M - 近6个月, 1Y - 近1年, 2Y - 近2年, 3Y - 近3年
        FundRateSummary("Open", "1Y").summarize()


class RunFundManager:

    @staticmethod
    def plot():
        from fundmgr import FundManagerPlot
        # 分布图
        p = FundManagerPlot()
        p.hist_exp()
        p.hist_rate_max()
        p.hist_rate_company()

    @staticmethod
    def summarize():
        from fundmgr import FundManagerSummary
        # 基金经理的统计信息
        f = FundManagerSummary()
        f.summarize()


class RunFundStar:

    @staticmethod
    def plot():
        from fundstar import FundStarPlot
        p = FundStarPlot()
        p.bar_stars()
        p.bar_s5_types()
        p.hist_commission()

    @staticmethod
    def summarize():
        from fundstar import FundStarSummary
        f = FundStarSummary()
        f.summarize()


if __name__ == "__main__":

    # RunFundManager.summarize()
    RunFundStar.plot()