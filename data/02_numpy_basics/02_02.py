import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return np.moveaxis(arr, -1, 1)

    # Alternative solution 1.
    # return np.transpose(arr, (0, 3, 1, 2))

    # Alternative solution 2.
    # return np.swapaxes(np.swapaxes(arr, 2, 3), 1, 2)


def dataset():
    # yield to_args(...)
    random.seed(34239284739)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t, h, w, d = [random.randint(1, 100) for _ in range(4)]
        arr = rnd.integers(0, 2**16 - 1, size=(t, h, w, 4), dtype=np.uint16)
        yield to_args(arr)
