import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    hist = np.bincount(arr)
    dist = hist[hist > 0] / hist.sum()
    out = dist * np.log2(dist)
    return float(-np.nansum(out))


def dataset():
    yield to_args(np.array([0, 1, 0, 1]))
    yield to_args(np.array([0, 1, 2, 3]))
    yield to_args(np.array([0, 0]))
    random.seed(897123490381)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(97):
        n = random.randint(1, 10000)
        p = random.randint(0, 9)
        q = random.randint(p + 1, 10)
        arr = rnd.integers(p, q, size=(n,), dtype=np.uint8)
        yield to_args(arr)
