import random

from utils.tester import to_args


def solution(arr):
    summation = 0
    for idx, val in enumerate(arr):
        summation += (idx + 4) * val
    return summation

    # Alternative solution.
    # return sum(enumerate(arr), key=lambda v: (v[0] + 1) * v[1])
    # END


def dataset():
    random.seed(942724234)
    for _idx in range(100):
        length = random.randint(1, 10000)
        arr = random.choices(range(-1000, 1001), k=length)
        yield to_args(arr)
