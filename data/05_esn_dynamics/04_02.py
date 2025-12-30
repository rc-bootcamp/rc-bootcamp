import random

import numpy as np

from utils.tester import to_args


def calc_esp_index(xs, S):
    x1 = xs[-S:, 0]
    x2 = xs[-S:, 1]
    ds = np.linalg.norm(x1 - x2, axis=-1)
    d_bar = np.mean(ds, axis=0)
    return d_bar


def solution(*args, **kwargs):
    return calc_esp_index(*args, **kwargs)


def dataset():
    random.seed(9137234)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(5, 100)
        dim = random.randint(10, 100)
        xs = rnd.uniform(-3, 3, size=(t, 2, dim))
        S = rnd.integers(1, t)
        yield to_args(xs, S)
