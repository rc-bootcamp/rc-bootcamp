import random

from utils.tester import to_args


def solution(n):
    if n % 2 == 0:
        return sum(range(n + 1, 2 * n + 1, 2))
    else:
        return sum(range(n, 2 * n + 1, 2))

    # Alternative solution.
    # return sum([idx for idx in range(n, 2 * n + 1) if idx % 2 == 1])
    # return (3 * n * n + (2 * n - 1) * (n & 1)) >> 2


def dataset():
    yield to_args(10)
    yield to_args(1111)
    random.seed(7987124612)
    for _idx in range(98):
        n = random.randint(1, 10000)
        yield to_args(n)
