import random

from utils.tester import to_args


def solution(a, b):
    try:
        return a // b
    except ZeroDivisionError:
        return -1
    # return (b == 0 and -1) or (a // b)  # Alternative solution.


def dataset():
    random.seed(8493789873)
    for _idx in range(100):
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        yield to_args(a, b)
