import random

from utils.tester import to_args


def solution(arr):
    return len(set(arr))

    # Alternative solution.
    # counter = {}
    # for val in arr:
    #     if not (val in counter):
    #         counter[val] = 1
    #     else:
    #         counter[val] += 1
    # return len(counter)


def dataset():
    yield to_args([1, 2, 1, 4, 1])
    yield to_args([2, 2])
    random.seed(847635891)
    for _idx in range(98):
        length = random.randint(1, 100)
        arr = random.choices(range(-100, 101), k=length)
        yield to_args(arr)
