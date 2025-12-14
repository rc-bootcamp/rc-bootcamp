import random
import string

from utils.tester import to_args


def solution(arr):
    return all(map(lambda v: type(v) is type(arr[0]), arr))

    # Alternative solution.
    return len(arr) == 0 or len(set(map(type, arr))) == 1


def dataset():
    yield to_args([1, 2, 3])
    yield to_args(["a", "b", "c"])
    yield to_args([1, 2, "a"])
    yield to_args([1, 2, "1"])
    yield to_args([])
    random.seed(6473979180)
    for _idx in range(95):
        length = random.randint(1, 1000)
        pos = random.random()
        if pos < 0.25:
            ls = random.choices(range(-1000, 1000), k=length)
        elif pos < 0.50:
            ls = random.choices(string.ascii_letters + string.digits, k=length)
        else:
            ls = random.choices(list(string.ascii_letters) + list(range(-100, 100)), k=length)
        yield to_args(ls)
