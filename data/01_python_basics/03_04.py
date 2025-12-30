import random
import string

from utils.tester import to_args


def solution(n):
    if n % 33 == 0:
        return True
    else:
        return "33" in str(n)


def dataset():
    yield to_args(66)
    yield to_args(3341)
    yield to_args(5133)
    yield to_args(4993)
    random.seed(1908729347)
    for _idx in range(96):
        if random.random() < 0.2:
            yield to_args(33 * random.randint(1, 3000000000))
        else:
            length = random.randint(1, 10)
            s = "".join(random.choices(string.digits[length == 1 :], k=length))
            yield to_args(int(s))
