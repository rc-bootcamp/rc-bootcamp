import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return arr.sum(axis=-1) - arr.min(axis=-1) - arr.max(axis=-1)

    # Alternative solution.
    # return np.sort(arr, axis=-1)[:, 1:-1].sum(axis=-1)


def dataset():
    yield to_args(np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]))
    yield to_args(np.array([[1, 1, 1, 1, 1, 1, 0, 0, 0, 0]]))
    random.seed(78293462342)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(98):
        n = random.randint(1, 1000)
        arr = rnd.integers(0, 100, size=(n, 10))
        yield to_args(arr)
