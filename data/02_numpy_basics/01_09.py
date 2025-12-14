import random

import numpy as np

from utils.tester import to_args


def solution(k, n):
    return np.roll(np.eye(n, dtype=np.int8), k - 1, axis=0)

    # Alternative solution.
    # return np.roll(np.eye(n, dtype=np.int8), 1 - k, axis=1)


def dataset():
    yield to_args(2, 3)
    random.seed(3287461283)
    for _idx in range(99):
        k = random.randint(1, 1000)
        n = random.randint(k, 1000)
        yield to_args(k, n)
