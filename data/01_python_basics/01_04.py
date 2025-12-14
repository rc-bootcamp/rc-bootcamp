import random

from utils.tester import to_args


def solution(c):
    return (c * 1.8) + 32


def dataset():
    random.seed(532218324)
    for _idx in range(100):
        c = random.randint(-100, 200)
        yield to_args(c)
