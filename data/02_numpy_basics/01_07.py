import random

import numpy as np

from utils.tester import to_args


def solution(mat_a, mat_b):
    return np.diag(np.diag(mat_a) * np.diag(mat_b))


def dataset():
    yield to_args(np.diag([1, 2]), np.diag([3, 4]))
    random.seed(3429784923432)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(99):
        length = random.randint(1, 1000)
        mat_a = np.diag(rnd.integers(-1000, 1000, (length,)))
        mat_b = np.diag(rnd.integers(-1000, 1000, (length,)))
        yield to_args(mat_a, mat_b)
