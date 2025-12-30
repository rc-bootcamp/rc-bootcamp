import random

import numpy as np

from utils.tester import to_args


def solution(y, d):
    mse = ((y - d) ** 2).mean(axis=0)
    std = np.std(d, axis=0)
    return np.sqrt(mse) / std

    # Alternative solution.
    # return (((y - d)**2).sum(axis=0) / ((d - d.mean(axis=0))**2).sum(axis=0))**0.5


def dataset():
    # yield to_args(...)
    random.seed(94587312904783)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(100, 1000)
        p = random.randint(1, 100)
        y = rnd.uniform(-1000, 1000, size=(t, p))
        d = rnd.uniform(-1000, 1000, size=(t, p))
        yield to_args(y, d)
