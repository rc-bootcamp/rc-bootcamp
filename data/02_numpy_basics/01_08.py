import random

import numpy as np

from utils.tester import to_args


def solution(arr_a, arr_b):
    return np.diag(arr_a) + np.diag(arr_b, 1) + np.diag(arr_b, -1)

    # Alternative solution.
    # mat_a = np.diag(arr_a)
    # mat_b = np.diag(arr_b, 1)
    # return mat_a + mat_b + mat_b.T


def dataset():
    yield to_args([1, 2, 3], [4, 5])
    random.seed(2783462897346)
    for _idx in range(99):
        len_b = random.randint(1, 999)
        arr_b = [random.randint(-1000, 1000) for _ in range(len_b)]
        arr_a = [random.randint(-1000, 1000) for _ in range(len_b + 1)]
        yield to_args(arr_a, arr_b)
