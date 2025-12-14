import random

from utils.tester import to_args


def solution(arr):
    return max(arr, key=lambda v: v[0] * v[1])


def dataset():
    yield to_args([(1, 2), (3, 4)])
    yield to_args([(4, 3), (6, 1)])
    random.seed(987439278432)
    for _idx in range(98):
        arr = []
        length = random.randint(1, 100)
        mul = 1
        for _ in range(length):
            left = random.randint(1, mul)
            right = mul // left + 1
            arr.append((left, right))
            mul = left * right
        random.shuffle(arr)
        yield to_args(arr)
