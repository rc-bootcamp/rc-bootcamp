import random

from utils.tester import to_args


def solution(arr_a, arr_b):
    return len(set(arr_a) & set(arr_b))


def dataset():
    yield to_args([1, 2, 3, 4, 5], [4, 5, 6])
    yield to_args([1, 2, 3, 4, 5], [10, 11, 12, 13])
    random.seed(74896378132)
    for _idx in range(98):
        len_a = random.randint(1, 10000)
        arr_a = random.choices(range(-1000, 1001), k=len_a)
        len_b = random.randint(1, 10000)
        arr_b = random.choices(range(-1000, 1001), k=len_b)
        yield to_args(arr_a, arr_b)
