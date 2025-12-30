import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    n = arr.shape[0]
    p = arr.shape[1] * arr.shape[2] * 3
    return arr[:, :, :, :-1].reshape(n, p)

    # Alternative solution.
    # return arr[..., :-1].reshape(arr.shape[0], -1)


def dataset():
    # yield to_args(...)
    random.seed(3598347958341)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        n, h, w = [random.randint(1, 100) for _ in range(3)]
        arr = rnd.integers(0, 256, size=(n, h, w, 4), dtype=np.uint8)
        yield to_args(arr)
