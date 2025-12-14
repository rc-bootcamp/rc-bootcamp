import random
import string

from utils.tester import to_args


def solution(s):
    arr = s.split()
    arr[0], arr[-1] = arr[-1], arr[0]
    return " ".join(arr)


def dataset():
    yield to_args("Hello world")
    yield to_args("To be or not to be")
    yield to_args("  wide      sentence  ")
    random.seed(49387598131)
    for _idx in range(97):
        length = random.randint(1, 1000)
        s = "".join(random.choices(string.ascii_letters, k=random.randint(0, 10)))
        while len(s) < length:
            if random.random() < 0.5:
                s += " " * random.randint(1, 10)
            else:
                s += "".join(random.choices(string.ascii_letters, k=random.randint(0, 10)))
        yield to_args(s[:length])
