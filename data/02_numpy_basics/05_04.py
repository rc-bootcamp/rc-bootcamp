import random

import numpy as np

from utils.tester import to_args


def solution(x, y):
    # DO NOT USE `np.linalg.lstsq` for your answer
    rss = np.linalg.lstsq(x, y, rcond=None)[1][0]
    r2 = 1 - rss / y.dot(y)
    return float(r2)

    # Alternative solution 1.
    # u, sigma, v = np.linalg.svd(x, full_matrices=False)
    # uy = np.dot(u.T, y)
    # return float(uy.dot(uy) / y.dot(y))

    # Alternative solution 2.
    # uy = x.T.dot(y)
    # uz = np.linalg.pinv(x).dot(y)  # `pinv` internally utilize SVD algorithm
    # return float(uy.dot(uz) / y.dot(y))


def dataset():
    random.seed(3248637432)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        p = random.randint(1, 100)
        n = random.randint(p, 1000)
        x = rnd.uniform(-10, 10, size=(n, p))
        y = rnd.uniform(-10, 10, size=(n,))
        w = rnd.uniform(-1, 1, size=(p,))
        c = random.random() * 0.25
        y = (1 - c) * y + c * x.dot(w)
        y -= y.mean()
        yield to_args(x, y)
