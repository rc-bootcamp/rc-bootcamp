import random

from utils.tester import to_args


def solution(arr):
    for idx in range(len(arr) - 1):
        if arr[idx] > arr[idx + 1]:
            return False
    return True

    # Alternative solution 1.
    # if len(arr) > 1:
    #     if arr[0] <= arr[1]:
    #         return solution(arr[1:])
    #     else:
    #         return False
    # else:
    #     return True

    # Alternative solution 2.
    # return sorted(arr) == arr


def dataset():
    yield to_args([2, 3, 10])
    yield to_args([2, 1, 2])
    yield to_args([3, 3, 5])
    yield to_args([10])
    random.seed(48971321323)
    for _idx in range(96):
        length = random.randint(1, 1000)
        arr = random.choices(range(-1000, 1001), k=length)
        if random.random() < 0.5:
            arr.sort()
        yield to_args(arr)
