import random

import numpy as np

from utils.tester import to_args


def solution(a, b, n):
    return a * np.logspace(0, 1, n, base=b / a)

    # Alternative solution 1.
    # return a * ((b / a)  ** np.linspace(0, 1, n))

    # Alternative solution 2.
    # return a * ((b / a) ** (np.arange(0, n) / (n - 1)))


def dataset():
    yield to_args(1.0, 8.0, 4)
    yield to_args(4.0, 1.0, 3)
    yield to_args(2.0, 2.0, 3)
    random.seed(40354309812)
    for _idx in range(97):
        a = random.uniform(0, 10000)
        b = random.uniform(0, 10000)
        n = random.randint(2, 100)
        yield to_args(a, b, n)
