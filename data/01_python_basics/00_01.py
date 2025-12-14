import random

from utils.tester import to_args


def solution(val):
    val = 6 * val
    return val


def dataset():
    random.seed(89374823)
    for _ in range(100):
        a = random.randint(-10000, 10000)
        yield to_args(a)
