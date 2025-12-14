import random

import numpy as np

from utils.tester import to_args


def create_parameter_set(th_min, th_max, num_split):
    th_new = th_min + ((np.arange(num_split) + 0.5) * (th_max - th_min)) / num_split
    return th_new


def solution(*args, **kwargs):
    return create_parameter_set(*args, **kwargs)


def dataset():
    random.seed(8359479473242)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        th_min = rnd.uniform(0, 1)
        th_max = rnd.uniform(th_min, 1)
        num_split = random.randint(10, 100)
        yield to_args(th_min, th_max, num_split)
