import random

from utils.tester import to_args


def solution(y):
    if y % 400 == 0:
        return True
    elif y % 100 == 0:
        return False
    elif y % 4 == 0:
        return True
    else:
        return False
    # return (y % 16) * (y % 25 < 1) < (y % 4 < 1)  # Alternative solution.


def dataset():
    random.seed(89179837219)
    for _idx in range(100):
        y = random.randint(0, 10000)
        yield to_args(y)
