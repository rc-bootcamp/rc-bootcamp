import random

from utils.tester import to_args


class Linear(object):
    def __init__(self, w_1, w_2, b):
        self.w_1, self.w_2, self.b = w_1, w_2, b

    def __call__(self, x, y):
        return self.w_1 * x + self.w_2 * y + self.b


def solution(w_1, w_2, b, x, y):
    # DO NOT CHANGE HERE.
    lin = Linear(w_1, w_2, b)
    return lin(x, y)


def dataset():
    yield to_args(1, 2, 3, 4, 5)
    random.seed(589376234923)
    for _idx in range(99):
        args = [random.randint(-100, 100) for _ in range(5)]
        yield to_args(*args)
