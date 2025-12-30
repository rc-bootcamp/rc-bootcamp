import random

from utils.tester import to_args


class Euclidean(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def norm(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5


def solution(*args):
    # DO NOT CHANGE HERE.
    point = Euclidean(*args)  # instance is created here!
    return point.norm()


def dataset():
    yield to_args(0.0, 3.0, 4.0)
    yield to_args(12.0, 5.0, 84.0)
    random.seed(9873294731)
    for _idx in range(98):
        args = [random.uniform(-100, 100) for _ in range(3)]
        yield to_args(*args)
