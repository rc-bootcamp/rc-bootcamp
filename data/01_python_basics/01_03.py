import random

from utils.tester import to_args


def solution(a, p):
    return (a ** (p - 1)) % p


def dataset():
    random.seed(432281349)
    for _idx in range(100):
        a = random.randint(1, 10000)
        p = random.randint(1, 10000)
        yield to_args(a, p)
