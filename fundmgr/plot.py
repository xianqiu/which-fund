import matplotlib.pyplot as plt

from .df import FundManagerDF


plt.rcParams['font.family'] = 'Microsoft YaHei'


class FundManagerPlot:

    def __init__(self, **kwargs):
        self.figsize = (10, 6)
        self.color = "skyblue"
        self.edgecolor = "black"
        self.fontsize = 16
        self.bins = 20
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.df = FundManagerDF().df

    def hist_exp(self):
        # 画直方图
        plt.figure(figsize=self.figsize)
        plt.hist(self.df.EXP, bins=self.bins,
                 color=self.color, edgecolor=self.edgecolor)
        plt.title("基金经理从业天数分布", fontsize=self.fontsize)
        plt.xlabel('从业天数', fontsize=self.fontsize)
        plt.ylabel('基金经理数量', fontsize=self.fontsize)
        plt.grid(axis='y')
        # 显示图形
        plt.tight_layout()
        plt.show()

    def hist_val_max(self):
        # 计算基金经理管理的基金规模（多支基金取Max）
        df = self.df.groupby("NAME")["FUND_VAL"].max().reset_index()
        # 选择规模在 [lb, ub] 的基金经理
        lb, ub = 1, 1000
        df = df[df["FUND_VAL"] >= lb]
        df = df[df["FUND_VAL"] <= ub]
        # 画图
        plt.figure(figsize=self.figsize)
        plt.hist(df.FUND_VAL, bins=self.bins,
                 color=self.color, edgecolor=self.edgecolor)
        plt.title("基金经理管理规模分布", fontsize=self.fontsize)
        plt.xlabel(f"基金规模 [min={lb}, max={ub}]", fontsize=self.fontsize)
        plt.ylabel('基金经理数量', fontsize=self.fontsize)
        plt.grid(axis='x')
        # 显示
        plt.tight_layout()
        plt.show()

    def hist_rate_max(self):
        # 计算基金经理任期的最大收益率（多支基金取median）
        df = self.df.groupby("NAME")["RATE_MAX"].median().reset_index()
        # 选择收益率在 [lb, ub] 的基金经理
        lb, ub = 0, 200
        df = df[df["RATE_MAX"] >= lb]
        df = df[df["RATE_MAX"] <= ub]
        # 画图
        plt.figure(figsize=self.figsize)
        plt.hist(df.RATE_MAX, bins=self.bins,
                 color=self.color, edgecolor=self.edgecolor)
        plt.title("基金经理任期的最大收益率分布", fontsize=self.fontsize)
        plt.xlabel(f"收益率（单位：%）", fontsize=self.fontsize)
        plt.ylabel('基金经理数量', fontsize=self.fontsize)
        plt.grid(axis='x')
        # 显示
        plt.tight_layout()
        plt.show()

    def hist_rate_company(self):
        # 计算基金公司的平均收益率（基金经理任期的最大收益率的中位数）
        df = self.df.groupby("COMPANY")["RATE_MAX"].median().reset_index()
        # 画图
        plt.figure(figsize=self.figsize)
        plt.hist(df.RATE_MAX, bins=self.bins,
                 color=self.color, edgecolor=self.edgecolor)
        plt.title("基金公司的收益率分布", fontsize=self.fontsize)
        plt.xlabel(f"收益率（单位：%）", fontsize=self.fontsize)
        plt.ylabel('基金公司数量', fontsize=self.fontsize)
        plt.grid(axis='x')
        # 显示
        plt.tight_layout()
        plt.show()