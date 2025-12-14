import random

import numpy as np

from utils.tester import to_args


def measure_leg_t(S, theta=1.0):
    measure = np.where((-theta <= S) & (S <= 0), 1.0 / theta, 0.0)
    return measure


def solution(*args, **kwargs):
    return measure_leg_t(*args, **kwargs)


def dataset():
    random.seed(324329281732)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        S = rnd.uniform(-20.0, 20.0, size=(10,))
        theta = rnd.uniform(0.1, 10.0)
        yield to_args(S, theta)
