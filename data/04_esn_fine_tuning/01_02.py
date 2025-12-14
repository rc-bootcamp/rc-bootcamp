import random

import numpy as np

from utils.tester import to_args


def calc_batch_nrmse(y, yhat):
    mse = y - yhat
    mse = (mse * mse).mean(axis=-2)
    var = y.var(axis=-2)
    return (mse / var) ** 0.5


def solution(*args, **kwargs):
    return calc_batch_nrmse(*args, **kwargs)


def dataset():
    random.seed(32493729123791)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dim = random.randint(1, 10)
        time_steps = random.randint(50, 100)
        ndim_x = random.randint(0, 5)
        ndim_y = random.randint(0, ndim_x)
        batch_x = [random.randint(1, 4) for _ in range(ndim_x)]
        batch_y = batch_x[len(batch_x) - ndim_y :]
        y = rnd.uniform(-1, 1, size=(*batch_x, time_steps, dim))
        yhat = rnd.uniform(-1, 1, size=(*batch_y, time_steps, dim))
        yield to_args(y, yhat)
