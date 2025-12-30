import random

from utils.tester import to_args


class Tarai(object):
    def __init__(self):
        self.cnt = 0
        self._cache = {}

    def __getitem__(self, key):
        self.cnt += 1
        x, y, z = key
        if key in self._cache:
            return self._cache[key]
        if x <= y:
            return y
        else:
            val = self[self[x - 1, y, z], self[y - 1, z, x], self[z - 1, x, y]]
            self._cache[key] = val
            return self._cache[key]


def solution(*args):
    # DO NOT CHANGE HERE.
    tar = Tarai()
    return tar[args], tar.cnt


def dataset():
    yield to_args(12, 6, 0)
    random.seed(4983798342)
    for _idx in range(99):
        args = [random.randint(0, 100) for _ in range(3)]
        if args[0] <= args[1] and random.random() < 0.9:
            args[0], args[1] = args[1], args[0]
        yield to_args(*args)
