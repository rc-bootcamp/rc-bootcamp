import random

import numpy as np

from utils.tester import to_args


def lorenz_func(z, a=10, b=28, c=8.0 / 3.0):
    assert z.shape[-1] == 3
    z_dot = np.zeros_like(z)
    z_dot[..., 0] = a * (z[..., 1] - z[..., 0])
    z_dot[..., 1] = z[..., 0] * (b - z[..., 2]) - z[..., 1]
    z_dot[..., 2] = z[..., 0] * z[..., 1] - c * z[..., 2]
    return z_dot


def solution(*args, **kwargs):
    return lorenz_func(*args, **kwargs)


def dataset():
    random.seed(1423708378)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(1, 100)
        z = rnd.uniform(-2, 2, size=(t, 3))
        yield to_args(z)
