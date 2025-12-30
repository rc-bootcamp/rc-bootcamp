import random

import numpy as np

from utils.tester import to_args


def solution(k, m, n):
    s = np.arange(1, k * k + 1).reshape(k, k)
    return np.tile(s, (m, n))

    # Alternative solution.
    # return ((np.arange(m * k) % k) * k)[:, None] + (np.arange(n * k) % k)[None, :] + 1


def dataset():
    yield to_args(2, 3, 4)
    random.seed(4768915452343)
    for _idx in range(99):
        k, m, n = [random.randint(1, 10) for _ in range(3)]
        yield to_args(k, m, n)
