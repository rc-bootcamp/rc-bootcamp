import random

from utils.tester import to_args


def solution(arr):
    return "+".join(map(lambda v: "({})".format(v) if v < 0 else str(v), arr))


def dataset():
    yield to_args([12, 34, 56])
    yield to_args([-123, 456])
    yield to_args([])
    yield to_args([12345])
    random.seed(8905452123)
    for _idx in range(96):
        length = random.randint(1, 1000)
        arr = random.choices(range(-1000, 1001), k=length)
        yield to_args(arr)
