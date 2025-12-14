import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return np.argmax(arr, axis=1)


def dataset():
    yield to_args(np.array([[0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]], dtype=np.uint8))
    random.seed(890739437203422)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(99):
        length = random.randint(1, 1000)
        indices = rnd.integers(0, 9, size=(length,))
        arr = np.eye(10, dtype=np.uint8)[indices]
        yield to_args(arr)
