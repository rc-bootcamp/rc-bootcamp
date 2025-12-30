import random

import numpy as np

from utils.tester import to_args


def transition_leg_s_nplr(N, tau=1.0):
    arange = np.arange(N)
    base = (2 * arange + 1) ** 0.5
    diff = arange[:, None] - arange[None, :]
    An = -base[:, None] * base[None, :]
    An[arange, arange] = 1
    An[diff <= 0] *= -1
    B = np.array(base)[:, None]
    An /= 2 * float(tau)
    B /= float(tau)
    P = np.array(base / (2 * float(tau)) ** 0.5)[:, None]
    return An, B, P


def solution(*args, **kwargs):
    return transition_leg_s_nplr(*args, **kwargs)


def dataset():
    random.seed(8912874923421723214)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        N = random.randint(1, 128)
        tau = rnd.uniform(0.1, 10.0)
        yield to_args(N, tau)
