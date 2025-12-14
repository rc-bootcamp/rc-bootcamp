import random

import numpy as np

from utils.tester import to_args


def solution(arr, k):
    val = np.argsort(arr, axis=None)
    return np.array(np.unravel_index(val[-k::], arr.shape)).T[::-1]


def dataset():
    yield to_args(np.array([[3.0, 7.0, 4.0], [6.0, 5.0, 8]]), 2)
    random.seed(39472938423)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(99):
        m, n = [random.randint(1, 100) for _ in range(2)]
        k = random.randint(1, min(100, m * n))
        arr = rnd.uniform(-1000, 1000, size=(m, n))
        yield to_args(arr, k)
