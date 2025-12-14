import random

from utils.tester import to_args


def solution(n):
    s = ""
    for idx in range(1, 10000):
        if len(s) > n:
            break
        s += str(idx)
    return s[n - 1]


def dataset():
    yield to_args(2)
    yield to_args(15)
    yield to_args(1000)
    random.seed(893749354)
    arr = random.choices(range(1, 10001), k=97)
    for v in arr:
        yield to_args(v)
