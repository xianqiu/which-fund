

if __name__ == "__main__":

    from pool.pipline import PoolPipline

    # p = PoolPipline()
    # p.process()

    from pool.df import FundPoolDF
    df = FundPoolDF().df

    from utils import DFPlot
    # DFPlot(df, "RATE_2Y").hist()

    from utils import DFSummary
    DFSummary(df, ["RATE_3Y", "RATE_2Y", "RATE_1Y"]).summarize()
