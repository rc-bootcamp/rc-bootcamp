import random

import numpy as np

from utils.tester import to_args


def transition_leg_t(N, theta=1.0):
    arange = np.arange(N)
    base = (2 * arange + 1) ** 0.5
    diff = arange[:, None] - arange[None, :]
    A = base[:, None] * base[None, :]
    A[(diff >= 0) | (diff % 2 == 0)] *= -1
    B = np.array(base)[:, None]
    A /= float(theta)
    B /= float(theta)
    return A, B


def solution(*args, **kwargs):
    return transition_leg_t(*args, **kwargs)


def dataset():
    random.seed(975329487918632)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        N = random.randint(1, 128)
        theta = rnd.uniform(0.1, 10.0)
        yield to_args(N, theta)
