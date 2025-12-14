import random
import string

from utils.tester import to_args


def solution(n, s):
    return "{:05d}.{:s}".format(n, s)
    # Alternative solution.
    # return f"{n:05d}.{s}"


def dataset():
    yield to_args(12, "py")
    yield to_args(98765, "txt")
    random.seed(59679845729)
    for _idx in range(98):
        n = random.randint(1, 99999)
        length = random.randint(1, 10)
        s = "".join(random.choices(string.ascii_letters, k=length))
        yield to_args(n, s)
