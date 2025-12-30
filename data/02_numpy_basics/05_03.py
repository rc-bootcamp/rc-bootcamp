import random

import numpy as np

from utils.tester import to_args


def solution(x, y):
    # DO NOT USE `np.linalg.lstsq` for your answer
    return float(np.linalg.lstsq(x, y, rcond=None)[1][0])

    # Alternative solution.
    # beta = np.linalg.inv(x.T @ x) @ (x.T @ y)
    # err = x.dot(beta) - y
    # return float((err * err).sum())


def dataset():
    random.seed(283467823)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        p = random.randint(1, 100)
        n = random.randint(p, 1000)
        x = rnd.uniform(-100, 100, size=(n, p))
        y = rnd.uniform(-100, 100, size=(n,))
        yield to_args(x, y)
