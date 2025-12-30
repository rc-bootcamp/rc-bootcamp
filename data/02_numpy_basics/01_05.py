import random

import numpy as np

from utils.tester import to_args


def solution(m, n):
    val = np.zeros((m, n), dtype=np.int8)
    val[2::3, ::3] = 2
    val[1::3, 1::3] = 2
    val[0::3, 2::3] = 2
    val[1::3, ::3] = 1
    val[::3, 1::3] = 1
    val[2::3, 2::3] = 1
    return val

    # Alternative solution 1.
    # return ((np.arange(m)[:, None] + np.arange(n)[None, :]) % 3).astype(np.uint8)

    # Alternative solution 2.
    # return np.fromfunction(lambda i, j: (i + j) % 3, (m, n)).astype(np.int8)

    # Alternative solution 3.
    # gy, gx = np.meshgrid(np.arange(n), np.arange(m))
    # return np.asarray(np.fmod(gx + gy, 3), np.int8)


def dataset():
    yield to_args(3, 3)
    yield to_args(1, 10)
    yield to_args(10, 1)
    random.seed(392472391432)
    for _idx in range(97):
        m = random.randint(1, 1000)
        n = random.randint(1, 1000)
        yield to_args(m, n)
