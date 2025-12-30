import random

from utils.tester import to_args


def solution(a, b):
    if b == 0:
        return -1
    else:
        return a // b


def dataset():
    random.seed(2498759874)
    for _idx in range(100):
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        yield to_args(a, b)
