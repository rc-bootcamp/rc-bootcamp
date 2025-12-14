import random

from utils.tester import to_args


def solution(arr_a, arr_b):
    summation = 0
    for a, b in zip(arr_a, arr_b, strict=False):
        summation += a * b
    return summation

    # Alternative solution.
    # return sum(zip(arr_a, arr_b), key=lambda v: v[0] * v[1])


def dataset():
    random.seed(648247392891)
    for _idx in range(100):
        length = random.randint(1, 10000)
        arr_a = random.choices(range(-100, 101), k=length)
        arr_b = random.choices(range(-100, 101), k=length)
        yield to_args(arr_a, arr_b)
