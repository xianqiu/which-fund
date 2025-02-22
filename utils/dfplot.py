import matplotlib.pyplot as plt


class DFPlot:

    def __init__(self, df, column, **kwargs):
        self.figsize = (10, 6)
        self.color = "skyblue"
        self.edgecolor = "black"
        self.fontsize = 16
        self.bins = 20
        self.font = "Microsoft YaHei"
        for k, v in kwargs.items():
            setattr(self, k, v)
        plt.rcParams['font.family'] = self.font
        self.df = df
        self.column = column

    def hist(self):
        # 画直方图
        plt.figure(figsize=self.figsize)
        plt.hist(self.df[self.column], bins=self.bins,
                 color=self.color, edgecolor=self.edgecolor)
        plt.title("Histogram", fontsize=self.fontsize)
        plt.xlabel(self.column, fontsize=self.fontsize)
        plt.ylabel('count', fontsize=self.fontsize)
        plt.grid(axis='y')
        # 显示图形
        plt.tight_layout()
        plt.show()