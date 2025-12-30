import random

from utils.tester import to_args


def solution(a, b):
    return (a + b) * (b - a + 1) // 2


def dataset():
    random.seed(198574343)
    for _idx in range(100):
        a = random.randint(1, 10000)
        b = random.randint(a, 10000)
        yield to_args(a, b)
