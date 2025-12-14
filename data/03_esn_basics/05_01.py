import random

import numpy as np

from utils.tester import to_args


def calc_nrmse(y, yhat):
    mse = y - yhat
    mse = (mse * mse).mean(axis=0)
    var = y.var(axis=0)
    return (mse / var) ** 0.5


def solution(*args, **kwargs):
    return calc_nrmse(*args, **kwargs)


def dataset():
    random.seed(3842793281623)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(10, 100)
        d = random.randint(1, 5)
        noise = random.uniform(0, 1)
        y = rnd.uniform(-1, 1, size=(t, d))
        yhat = y + noise * rnd.uniform(-1, 1, size=(t, d))
        yield to_args(y, yhat)
