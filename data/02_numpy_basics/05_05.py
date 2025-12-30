import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    arr = arr - arr.mean(axis=0, keepdims=True)
    eigs = np.linalg.eig(arr.T.dot(arr))[0]
    es = abs(eigs)
    es *= 1 / sum(es)
    return float(1 / (sum(es**2)))


def dataset():
    random.seed(890574395432)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        p = random.randint(1, 100)
        n = random.randint(p, 1000)
        x = rnd.uniform(-10, 10, size=(n, p))
        yield to_args(x)
