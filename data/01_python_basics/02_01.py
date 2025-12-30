import random

from utils.tester import to_args


def solution(a, b, c):
    return (a % c) == (b % c)
    # return not ((a - b) % c)  # Alternative solution.


def dataset():
    random.seed(91092784027)
    for _idx in range(100):
        a = random.randint(1, 10000)
        b = random.randint(1, 10000)
        c = random.randint(1, 10)
        yield to_args(a, b, c)
