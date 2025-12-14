import random

import numpy as np

from utils.tester import to_args


def create_grid_search_setup(us, sigma, phi, rho):
    vs = sigma[:, None, None, None, None] * us + phi[:, None, None, None]
    rho_new = rho[:, None]
    return vs, rho_new


def solution(*args, **kwargs):
    return create_grid_search_setup(*args, **kwargs)


def dataset():
    random.seed(4389574398734923)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(20, 50)
        k, l2, m = [random.randint(1, 20) for _ in range(3)]
        us = rnd.uniform(0.0, 1.0, size=(t, 1))
        sigma = rnd.uniform(0.0, 1.0, size=(k,))
        phi = rnd.uniform(0.0, 1.0, size=(l2,))
        rho = rnd.uniform(0.0, 1.0, size=(m,))
        yield to_args(us, sigma, phi, rho)
