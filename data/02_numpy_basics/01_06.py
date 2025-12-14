import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    return np.eye(10, dtype=np.int8)[arr]


def dataset():
    yield to_args([2, 3])
    random.seed(789638937264)
    for _idx in range(99):
        length = random.randint(1, 1000)
        arr = [random.randint(0, 9) for _ in range(length)]
        yield to_args(arr)
