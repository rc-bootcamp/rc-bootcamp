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


def solution(*args):
    # DO NOT CHANGE HERE.
    x1, y1, z1, x2, y2, z2, x3, y3, z3 = args
    p1 = Euclidean(x1, y1, z1)
    p2 = Euclidean(x2, y2, z2)
    p3 = Euclidean(x3, y3, z3)
    return abs((p3 - p1) * (p2 - p1)) * 0.5


def dataset():
    yield to_args(1.0, 1.0, 1.0, 4.0, 5.0, 1.0, -3.0, 4.0, 1.0)
    random.seed(198273412123)
    for _idx in range(99):
        a1 = [random.uniform(-100, 100) for _ in range(3)]
        a2 = [random.uniform(-100, 100) for _ in range(3)]
        a3 = [random.uniform(-100, 100) for _ in range(3)]
        yield to_args(*a1, *a2, *a3)
