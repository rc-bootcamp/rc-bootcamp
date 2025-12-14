import random

import numpy as np

from utils.tester import to_args


class Legendre(object):
    def __init__(self, xs):
        self.xs = xs
        self._caches = {}
        self._caches[0] = 1
        self._caches[1] = self.xs

    def __getitem__(self, deg):
        assert deg >= 0
        if deg not in self._caches:
            self._caches[deg] = self._calc(deg)
        return self._caches[deg]

    def _calc(self, n: int):
        res = ((2 * n - 1) / n) * self.xs * self[n - 1]
        res -= ((n - 1) / n) * self[n - 2]
        return res


def solution(us, n):
    poly = Legendre(us)
    return poly[n]


def dataset():
    random.seed(54395749382)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(10, 1000)
        n = random.randint(1, 20)
        arr = rnd.uniform(-1, 1, size=(t,))
        yield to_args(arr, n)
