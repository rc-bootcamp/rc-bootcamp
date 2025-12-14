import random

from utils.tester import to_args


def solution(arr):
    counter = {}
    for val in arr:
        if val not in counter:
            counter[val] = 1
        else:
            counter[val] += 1
    return max(counter.values())

    # Alternative solution.
    # from collections import Counter
    # return max(Counter(arr).values())


def dataset():
    yield to_args([1, 2, 1, 1, 1])
    yield to_args([3, 3, 4, 4, 6])
    yield to_args([2, 2])
    random.seed(8719457832)
    for _idx in range(97):
        length = random.randint(1, 10000)
        arr = random.choices(range(-1000, 1001), k=length)
        yield to_args(arr)
