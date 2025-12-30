import random

from utils.tester import to_args


class Euclidean(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def norm(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def __abs__(self):
        return self.norm()

    def __sub__(self, other):
        return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return self.__class__(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )


class Manhattan(Euclidean):
    def norm(self):
        return abs(self.x) + abs(self.y) + abs(self.z)


def solution(*args):
    # DO NOT CHANGE HERE.
    p = Manhattan(*args)
    return abs(p)


def dataset():
    yield to_args(0, 3, 4)
    random.seed(392874392144)
    for _idx in range(99):
        args = [random.randint(-100, 100) for _ in range(3)]
        yield to_args(*args)
