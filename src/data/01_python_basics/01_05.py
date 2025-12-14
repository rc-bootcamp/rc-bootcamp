import random

from utils.tester import to_args


def solution(a, b, c):
    return (-b + (b**2 - 4 * a * c) ** 0.5) / (2 * a)


def dataset():
    random.seed(479587161)
    for _idx in range(100):
        while True:
            a = random.randint(-100, 100)
            b = random.randint(-100, 100)
            c = random.randint(-100, 100)
            if (a * b * c != 0) and (b**2 > 4 * a * c):
                break
        yield to_args(a, b, c)
