import random

from utils.tester import to_args


def solution(arr):
    return arr == arr[::-1]

    # Alternative solution.
    # return all(map(lambda t: t[0] == t[1], zip(arr, arr[::-1])))


def dataset():
    yield to_args([0, 1, 0])
    yield to_args([2, 3, 4, 5])
    yield to_args([1])
    random.seed(49874928343)
    for _idx in range(97):
        length = random.randint(1, 1000)
        arr = random.choices(range(-1000, 1001), k=length)
        if length > 1 and random.random() < 0.5:
            half = length // 2
            rev = arr[half::-1] if length % 2 == 0 else arr[half + 1 :: -1]
            if random.random() < 0.5:
                arr = arr[:half] + rev
        yield to_args(arr)
