import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return np.full_like(arr, arr[0, 0])
    # return np.zeros(arr.shape, dtype=arr[0, 0]) + arr[0, 0]
    # return np.ones(arr.shape, dtype=arr[0, 0]) * arr[0, 0]


def dataset():
    yield to_args(np.eye(3)[:1] * 2)
    yield to_args(np.array([[4, 3, 2], [2, 3, 4]]))
    random.seed(4354890712983)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(98):
        m = random.randint(1, 1000)
        n = random.randint(1, 1000)
        if random.random() < 0.5:
            yield to_args(rnd.uniform(-10000, 10000, size=(m, n)))
        else:
            yield to_args(rnd.integers(-10000, 10001, size=(m, n)))
