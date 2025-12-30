import random

import numpy as np

from utils.tester import to_args


def narma_func(us, y_init, alpha=0.3, beta=0.05, gamma=1.5, delta=0.1, mu=0.25, kappa=0.25):
    assert us.shape[0] > 10
    assert y_init.shape[0] == 10
    assert y_init.shape[1:] == us.shape[1:]
    vs = mu * us + kappa
    ys = np.zeros_like(vs)
    ys[:10] = y_init
    for idx in range(10, ys.shape[0]):
        ys[idx] += alpha * ys[idx - 1]
        ys[idx] += beta * ys[idx - 1] * np.sum(ys[idx - 10 : idx], axis=0)
        ys[idx] += gamma * vs[idx - 10] * vs[idx - 1]
        ys[idx] += delta
    return ys


def solution(*args, **kwargs):
    return narma_func(*args, **kwargs)


def dataset():
    random.seed(732896419283741)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(1, 100)
        d = random.randint(1, 10)
        us = rnd.uniform(-0.1, 0.1, size=(t + 10, d))
        y_init = rnd.uniform(0.0, 0.01, size=(10, d))
        yield to_args(us, y_init)
