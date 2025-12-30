import random

import numpy as np

from utils.tester import to_args


def convert_us_into_vs(us, sigma, phi):
    assert len(sigma) == len(phi)
    vs = sigma[:, None, None] * us + phi[:, None, None]
    return vs


def solution(*args, **kwargs):
    return convert_us_into_vs(*args, **kwargs)


def dataset():
    random.seed(574398574931)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        lt = random.randint(1, 100)
        lp = random.randint(1, 10)
        arr = rnd.uniform(-1, 1, size=(lt, 1))
        sigma = rnd.uniform(0, 1, size=(lp,))
        phi = rnd.uniform(0, 1, size=(lp,))
        yield to_args(arr, sigma, phi)
