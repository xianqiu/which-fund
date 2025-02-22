
class DFSummary(object):

    def __init__(self, df, column, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.df = df
        # column可以是一列或多列
        self.column = column if isinstance(column, list) else [column]
        self._check()

    def _check(self):
        # 检查列是否在df中
        miss = set(self.column) - set(self.df.columns.tolist())
        if miss != set():
            raise ValueError(f"Columns {miss} not found in dataframe.")

    def _statistics(self, col):
        df = self.df[col].dropna()
        num = len(df)
        mean = round(df.mean(), 2)
        std = round(df.std(), 2)
        lb = round(df.min(), 2)
        ub = round(df.max(), 2)
        quantile_levels = [0.2, 0.5, 0.8]
        quantiles = df.quantile(quantile_levels).values.tolist()
        # 结果保留两位小数
        quantiles = [round(q, 2) for q in quantiles]
        return {
            "num": num,
            "mean": mean,
            "std": std,
            "lb": lb,
            "ub": ub,
            "quantile_levels": quantile_levels,
            "quantiles": quantiles,
        }

    def _summarize(self, col):
        """
        统计数据
        """
        stats = self._statistics(col)
        print(f"==== [{col}] Summary ====")
        print(f"|--  Count: {stats['num']}, Mean: {stats['mean']}, Std: {stats['std']}")
        print(f"|--  Lower Bound: {stats['lb']}, Upper Bound: {stats['ub']}")
        print(f"|--  Quantile Levels: {stats['quantile_levels']}")
        print(f"|--  Quantile Values: {stats['quantiles']}")

    def summarize(self):
        for col in self.column:
            self._summarize(col)