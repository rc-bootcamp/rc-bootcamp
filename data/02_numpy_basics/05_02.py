import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return arr / np.linalg.norm(arr, axis=-1, keepdims=True)


def dataset():
    yield to_args(np.eye(3) * 2)
    random.seed(938742423)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(99):
        n = random.randint(1, 1000)
        p = random.randint(1, 1000)
        arr = rnd.uniform(-100, 100, size=(n, p))
        yield to_args(arr)
