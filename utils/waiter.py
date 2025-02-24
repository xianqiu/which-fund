import time

import numpy as np

from .logger import logger


class WT(object):

    mean = 1_000  # 单位: 毫秒
    std = 500
    lb = 200  # 单位: 毫秒
    ub = 10_000  # 单位: 毫秒
    rho = 3

    @classmethod
    def _wait_time(cls):
        # 单位: 毫秒
        mean = np.random.uniform(cls.mean, cls.rho * cls.std)
        std = np.random.uniform(cls.std, cls.rho * cls.std)
        wait_time = np.random.normal(mean, std)

        if wait_time < cls.lb:
            wait_time = cls.lb
        if wait_time > cls.ub:
            wait_time = cls.ub

        return wait_time

    @classmethod
    def wait(cls):
        wait_time = cls._wait_time()  # 单位:毫秒
        logger.info(f"[WAIT] {wait_time:.2f} ms ...")
        time.sleep(wait_time / 1000)