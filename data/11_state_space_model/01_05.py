import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return arr


def dataset():
    yield to_args(...)
    random.seed(...)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        a = random.randint(1, 1000)
        b = random.randint(1, 1000)
        arr = rnd.uniform(-100, 100, size=(a, b))
        yield to_args(arr)
