import random

from utils.tester import to_args


def solution(a, b):
    if a < 57 and b < 57:
        ans = a + b
    else:
        ans = 5
    return ans


def dataset():
    random.seed(189723987421)
    for _idx in range(100):
        a = random.randint(-1000, 1000)
        b = random.randint(-1000, 1000)
        yield to_args(a, b)
