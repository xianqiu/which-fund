import matplotlib.pyplot as plt

from .df import FundStarDF


plt.rcParams['font.family'] = 'Microsoft YaHei'


class FundStarPlot:

    def __init__(self, **kwargs):
        self.figsize = (10, 6)
        self.color = "skyblue"
        self.edgecolor = "black"
        self.fontsize = 16
        self.bins = 20
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.df = FundStarDF().df

    def bar_stars(self, by=None):
        """ 评级的分布图
        :param by: SHZQ - 上海证券, ZSZQ - 招商证券, JAJX - 济安金信;
                   MEDIAN - 取三个评级的中位数
        """
        info = {
            "SHZQ": "上海证券",
            "ZSZQ": "招商证券",
            "JAJX": "济安金信",
            "MEDIAN": "综合",
        }
        if by is None:
            by = "MEDIAN"
            df = self.df
            df[f"STAR_{by}"] = self.df[["STAR_SHZQ", "STAR_ZSZQ", "STAR_JAJX"]].fillna(0).median(axis=1)
        else:
            assert by in ["SHZQ", "ZSZQ", "JAJX"], f"{by} is not in [SHZQ, ZSZQ, JAJX]"

        df = self.df[f"STAR_{by}"].dropna().astype(int)
        df = df.groupby(df).size().reset_index(name='COUNT')
        plt.bar(df[f"STAR_{by}"], df.COUNT, color=self.color, edgecolor=self.edgecolor)
        plt.title(f"{info[by]}评级数量统计", fontsize=self.fontsize)
        plt.xlabel("星级", fontsize=self.fontsize)
        plt.ylabel("基金数", fontsize=self.fontsize)
        plt.grid(axis='y')
        plt.show()

    def bar_s5_types(self):
        """ 五星基金类型的分布图
        """
        df = self.df
        df["STARS"] = self.df[["STAR_SHZQ", "STAR_ZSZQ", "STAR_JAJX"]].fillna(0).median(axis=1)
        df = df[df["STARS"] >= 5]
        df = df.groupby("TYPE").size().reset_index(name='COUNT')
        df = df.sort_values(by="COUNT", ascending=True)
        # 画柱状图
        plt.figure(figsize=self.figsize)
        plt.barh(df.TYPE, df.COUNT, color=self.color, edgecolor=self.edgecolor)
        plt.title("五星基金的类型统计", fontsize=self.fontsize)
        plt.grid(axis='x')
        plt.show()

    def hist_commission(self):
        """ 手续费的分布图
        """
        df = self.df
        df = df.COMMITION.dropna()
        plt.figure(figsize=self.figsize)
        plt.hist(df * 100, bins=self.bins, color=self.color, edgecolor=self.edgecolor)
        plt.title("基金手续费的分布", fontsize=self.fontsize)
        plt.xlabel("手续费（单位：%）", fontsize=self.fontsize)
        plt.ylabel("基金数", fontsize=self.fontsize)
        plt.grid(axis='y')
        plt.show()
