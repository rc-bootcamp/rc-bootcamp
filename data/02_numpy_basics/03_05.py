import random

import numpy as np

from utils.tester import to_args


def solution(arr_a, arr_b):
    return np.where(arr_a > arr_b, arr_a, arr_b)

    # Alternative solution.
    # return np.maximum(arr_a, arr_b)


def dataset():
    random.seed(94075948375043)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        m, n = [random.randint(1, 100) for _ in range(2)]
        arr_a = rnd.uniform(-1000, 1000, (m, n))
        arr_b = rnd.uniform(-1000, 1000, (m, n))
        yield to_args(arr_a, arr_b)
