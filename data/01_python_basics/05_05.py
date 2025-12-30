import random

from utils.tester import to_args


def solution(n):
    def operator(m):
        return m // 2 if m % 2 == 0 else 3 * m + 1

    cnt = 0
    while n != 1:
        n = operator(n)
        cnt += 1
    return cnt


def dataset():
    yield to_args(3)
    yield to_args(1)
    yield to_args(27)
    random.seed(4937294832)
    for _idx in range(97):
        n = random.randint(1, 10000)
        yield to_args(n)
