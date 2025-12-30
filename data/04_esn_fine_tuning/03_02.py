import random

import numpy as np

from utils.tester import to_args


def reshape_rho(rho):
    rho_new = rho[:, None]
    return rho_new


def solution(*args, **kwargs):
    return reshape_rho(*args, **kwargs)


def dataset():
    random.seed(34493274923)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dims = random.randint(1, 100)
        rhos = rnd.uniform(0.0, 1.0, size=(dims,))
        yield to_args(rhos)
