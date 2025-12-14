import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    vel = arr[1:] - arr[:-1]
    return np.concatenate([arr[1:], vel], axis=-1)


def dataset():
    # yield to_args(...)
    random.seed(7124598328614)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(1, 1000)
        n = random.randint(1, 10)
        arr = rnd.integers(-1000, 1000, size=(t, n, 3))
        yield to_args(arr)
