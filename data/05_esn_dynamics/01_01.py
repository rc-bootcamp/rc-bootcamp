import random

import numpy as np

from utils.tester import to_args


def henon_func(z, a=1.4, b=0.3):
    assert z.shape[-1] == 2
    z_out = np.zeros_like(z)
    z_out[..., 0] = 1.0 - a * (z[..., 0] ** 2) + z[..., 1]
    z_out[..., 1] = b * z[..., 0]
    return z_out


def solution(*args, **kwargs):
    return henon_func(*args, **kwargs)


def dataset():
    random.seed(6541651354564)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(1, 100)
        z = rnd.uniform(-2, 2, size=(t, 2))
        yield to_args(z)
