import random

from utils.tester import to_args


def solution(a0, a1, *args):
    return (a0 + a1) * args[-1]


def dataset():
    yield to_args(1, 2, 3)
    yield to_args(4, 3, 2, 5)
    random.seed(9749372352)
    for _idx in range(98):
        length = random.randint(3, 1001)
        arr = random.choices(range(-1000, 1001), k=length)
        yield to_args(*arr)
