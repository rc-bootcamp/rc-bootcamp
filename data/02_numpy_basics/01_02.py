import random

import numpy as np

from utils.tester import to_args


def solution(a, d, n):
    return np.arange(a, a + d * n, d)
    return a + np.arange(n) * d


def dataset():
    yield to_args(5, 3, 4)
    yield to_args(4, -2, 3)
    random.seed(453987549387)
    for _idx in range(98):
        a = random.randint(-10000, 10000)
        d = random.randint(-10000, 10000)
        n = random.randint(1, 10000)
        yield to_args(a, d, n)
