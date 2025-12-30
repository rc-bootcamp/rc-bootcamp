import random
import string

from utils.tester import to_args


def solution(arr):
    length = len(arr)
    if length == 0:
        return 0
    else:
        if type(arr[0]) is list:
            return solution(arr[0]) + solution(arr[1:])
        else:
            return 1 + solution(arr[1:])


def nested_arr(arr, count):
    if count == 0:
        return arr
    if random.random() < 0.75:
        if random.random() < 0.5:
            val = random.randint(-1000, 1000)
        else:
            length = random.randint(1, 4)
            val = "".join(random.choices(string.ascii_letters, k=length))
        arr.append(val)
        return nested_arr(arr, count - 1)
    else:
        new_arr = []
        arr.append(nested_arr(new_arr, count))
        return arr


def dataset():
    yield to_args([[0], [1, 2, 3]])
    yield to_args([0, 1, [2], [[[3]]]])
    yield to_args([0, 1, "c", "ab"])
    yield to_args([[[]]])
    random.seed(3242487323)
    for _idx in range(96):
        arr = []
        length = random.randint(1, 1000)
        nested_arr(arr, length)
        yield to_args(arr)
