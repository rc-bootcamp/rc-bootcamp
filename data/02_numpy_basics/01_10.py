import random

import numpy as np

from utils.tester import to_args


def solution(n):
    n_abs = abs(n)
    m = n_abs * (n_abs + 1) / 2
    mat = np.zeros((n_abs, n_abs), dtype=np.int32)
    arr = np.arange(1, m + 1, dtype=np.int32)
    if n > 0:
        mat[np.triu_indices_from(mat)] = arr
    elif n < 0:
        mat[np.tril_indices_from(mat)] = arr
    return mat


def dataset():
    yield to_args(2)
    yield to_args(-3)
    random.seed(53498753492)
    for _idx in range(98):
        n = random.randint(1, 1000)
        if random.random() < 0.5:
            n *= -1
        yield to_args(n)
