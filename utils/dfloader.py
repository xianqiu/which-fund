import time
from pathlib import Path

import pandas as pd

from .logger import logger


class DFLoader:

    def __init__(self, **kwargs):
        self.df = None
        self.header = None
        self.expire = 30  # 过期天数
        self.file_dir = Path("./data")
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.load()

    def _get_filename(self):
        """获取数据文件的文件名称。
        如果文件不存在则返回 None；如果有多个文件，返回最新的文件名。
        """
        prefix = f"{self.__class__.__name__}"
        filenames = []
        for filename in Path.iterdir(self.file_dir):
            if filename.name.startswith(prefix):
                filenames.append(filename.name)
        if len(filenames) == 0:
            return None
        # 按照文件名中的日期排序，最新的在前面
        filenames.sort(key=lambda x: x.split('_')[-1].split('.')[0], reverse=True)
        # 返回最新的元素
        return filenames[0]

    def _is_expired(self, filename):
        """判断数据是否过期。
        注意：如果文件不存在，也认为数据过期。
        """
        if filename is None:
            return True
        date = filename.split("_")[-1].split(".")[0]
        date = time.strptime(date, "%Y%m%d")
        date = time.mktime(date)
        now = time.time()
        return (now - date) > self.expire * 24 * 60 * 60

    def _remove_expired(self):
        """删除过期的数据文件。
        注意：至少保留一个文件（无论是否过期）。
        """
        prefix = f"{self.__class__.__name__}"
        filenames = []
        for filename in Path.iterdir(self.file_dir):
            if filename.name.startswith(prefix):
                filenames.append(filename.name)
        # 按照文件名中的日期排序，最新的在前面
        filenames.sort(key=lambda x: x.split('_')[-1].split('.')[0], reverse=True)
        if len(filenames) <= 1:
            return
        for filename in filenames[1:]:
            Path.unlink(self.file_dir / filename)

    def load(self):
        """加载数据"""
        # 如果数据过期, 则更新并保存数据
        # 注意: 如果数据不存在, 也认为数据过期
        use_cache = True
        if self._is_expired(self._get_filename()):
            use_cache = False
            self.get()
            self.save()
            self._remove_expired()

        self.df = pd.read_csv(self.file_dir / self._get_filename())
        logger.info(f"[Load]: data = {self.__class__.__name__}, use_cache = {use_cache}")

    def save(self):
        """保存数据
        """
        if self.df is None or self.df.empty:
            logger.info("[Get]: FAIL")
            return
        # 文件名为 class 名称 + 日期
        date = time.strftime("%Y%m%d", time.localtime())
        filename = f"{self.__class__.__name__}_{date}.csv"
        if self.header is None:
            self.header = self.df.columns
        self.df.to_csv(self.file_dir / filename,
                       header=self.header, index=False)
        logger.info("[Get]: SUCCESS")

    def get(self):
        """获取数据"""
        # self.df = ...
        pass

    def update(self):
        """更新数据"""
        self.get()
        self.save()
        # 删除过期的数据
        self._remove_expired()
        # 重新加载数据
        self.df = pd.read_csv(self.file_dir / self._get_filename())
        logger.info(f"[Update]: SUCCESS")

        return self

    def get_cache_date(self):
        filename = self._get_filename()
        if filename is None:
            return None
        date = filename.split("_")[-1].split(".")[0]
        return date