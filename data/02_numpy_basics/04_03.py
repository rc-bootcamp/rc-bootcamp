import random

import numpy as np

from utils.tester import to_args


def solution(m, arr):
    out = np.pad(arr, (m - 1, 0), mode="edge")
    return np.convolve(out, np.full(m, 1 / m), mode="valid")


def dataset():
    yield to_args(3, np.array([1, 1, 1, 4, 7]))
    random.seed(8590273432432)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(99):
        t = random.randint(1, 1000)
        m = random.randint(1, t)
        arr = rnd.uniform(-10, 10, size=(t,))
        yield to_args(m, arr)
