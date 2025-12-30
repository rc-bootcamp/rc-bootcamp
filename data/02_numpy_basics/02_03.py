import random

import numpy as np

from utils.tester import to_args


def solution(k, arr):
    for _ in range(k - 2):
        arr = arr[:, None, ..., :]
    return arr

    # Alternative solution 1.
    # for _ in range(k - 2):
    #     arr = np.expand_dims(arr, axis=1)
    # return arr

    # Alternative solution 2.
    # sli = (slice(None),) + (None,) * (k - 2) + (slice(None),)
    # return arr[sli]

    # Alternative solution 3.
    # t, p = arr.shape
    # return arr.reshape(t, *(1,) * (k - 2), p)


def dataset():
    yield to_args(3, np.arange(1, 5).reshape(2, 2))
    random.seed(3243212)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(99):
        k = random.randint(2, 10)
        t, p = [random.randint(1, 100) for _ in range(2)]
        arr = rnd.integers(-1000, 1000, size=(t, p))
        yield to_args(k, arr)
