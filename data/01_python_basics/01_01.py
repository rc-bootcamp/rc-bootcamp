import random

from utils.tester import to_args


def solution(a, b):
    return (a - b) * (3 * a + 2 * b)


def dataset():
    random.seed(5493879182)
    for _idx in range(100):
        a = random.randint(-10000, 10000)
        b = random.randint(-10000, 10000)
        yield to_args(a, b)
