import random

from utils.tester import to_args


def solution(arr):
    counter = {}
    for val in arr:
        if val not in counter:
            counter[val] = 1
        else:
            counter[val] += 1
    acc = []
    for key, val in counter.items():
        acc.append(key + val)
    return max(acc)

    # Alternative solution.
    # from collections import Counter
    # return max(Counter(arr).items(), key=lambda t: t[0] + t[1])[0]


def dataset():
    yield to_args([1, 1, 1, 3, 3, 4])
    yield to_args([1, 2, 1, 2, 1, 3])
    yield to_args([2, 2, 3, 3, 4, 4])
    random.seed(5439278932)
    for _idx in range(97):
        length = random.randint(1, 100)
        left = random.randint(-10, 10)
        right = random.randint(left, 10)
        arr = random.choices(range(left, right + 1), k=length)
        yield to_args(arr)
