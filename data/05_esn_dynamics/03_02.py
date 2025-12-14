import random

import numpy as np

from utils.tester import to_args


def dlogistic_func(z, a=3.0):
    assert z.shape[-1] == 1
    dz = a * (1 - 2 * z)
    return dz


def solution(*args, **kwargs):
    return dlogistic_func(*args, **kwargs)


def dataset():
    random.seed(76976378)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(1, 100)
        z = rnd.uniform(-2, 2, size=(t, 1))
        yield to_args(z)
