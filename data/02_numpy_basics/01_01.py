import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    vmax, vmin = max(arr), min(arr)
    if np.iinfo(np.int64).min <= vmin <= vmax <= np.iinfo(np.int64).max:
        return np.array(arr, dtype=np.int64)
    else:
        return np.array(arr, dtype=np.float64)


def dataset():
    np.eye(3)
    yield to_args([2**100, 10])
    yield to_args([2**60, 10])
    yield to_args([-(2**63), 2**63 - 1])
    yield to_args([-(2**63), 2**63])

    random.seed(49783594312)
    for _idx in range(96):
        length = random.randint(1, 10000)
        if random.random() < 0.5:
            arr = [random.randint(-(2**63), 2**63 - 1) for _ in range(length)]
        else:
            arr = [random.randint(-(10**100), 10**100) for _ in range(length)]
        yield to_args(arr)
