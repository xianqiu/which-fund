import matplotlib.pyplot as plt

from .df import OpenFundRateDF, HKFundRateDF, CNFundRateDF, HBFundRateDF


plt.rcParams['font.family'] = 'Microsoft YaHei'


class FundRatePlot:

    sources = {
        "Open": OpenFundRateDF,  # 开放基金
        "HK": HKFundRateDF,  # 香港基金
        "HB": HBFundRateDF,  # 货币基金
        "CN": CNFundRateDF,  # 场内基金
    }

    columns = {
        "6M": "RATE_6M",  # 最近六个月
        "1Y": "RATE_1Y",  # 最近一年
        "2Y": "RATE_2Y",  # 最近两年
        "3Y": "RATE_3Y",  # 最近三年
    }

    def __init__(self, source: str, span="1Y", **kwargs):
        self.title = self.sources[source].remark
        self.figsize = (10, 6)
        self.color = "skyblue"
        self.edgecolor = "black"
        self.fontsize = 16
        self.bins = 20
        for k, v in kwargs.items():
            setattr(self, k, v)
        assert source in self.sources.keys(), f"source must be in {list(self.sources.keys())}"
        assert span in self.columns.keys(), f"span must be in {list(self.columns.keys())}"
        self.column = self.columns[span]
        self.df = self.sources[source]().df

    def hist(self):
        # 画直方图
        plt.figure(figsize=self.figsize)
        plt.hist(self.df[self.column], bins=self.bins,
                 color=self.color, edgecolor=self.edgecolor)
        plt.title(self.title, fontsize=self.fontsize)
        plt.xlabel('收益率 (单位: %)', fontsize=self.fontsize)
        plt.ylabel('数量', fontsize=self.fontsize)
        plt.grid(axis='y')
        # 显示图形
        plt.tight_layout()
        plt.show()

    @classmethod
    def print_sources(cls):
        # 打印所有数据源
        for k, v in cls.sources.items():
            print(f"source = {k}, value = {v.__name__}, remark = {v.remark}")