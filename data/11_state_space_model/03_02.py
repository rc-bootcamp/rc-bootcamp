import random

import numpy as np

from utils.tester import to_args


def measure_leg_s(S, tau=1.0):
    measure = np.exp(S / tau) * (1 / tau)
    return measure


def solution(*args, **kwargs):
    return measure_leg_s(*args, **kwargs)


def dataset():
    random.seed(849871293213)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        S = rnd.uniform(-20.0, 20.0, size=(10,))
        tau = rnd.uniform(0.1, 10.0)
        yield to_args(S, tau)
