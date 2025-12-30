import random

from utils.tester import to_args


def solution(w, h):
    bmi = w / (h / 100.0) ** 2
    return 20.0 <= bmi <= 25.0


def dataset():
    random.seed(9879281434)
    for _idx in range(100):
        w = random.randint(30, 200)
        h = random.randint(100, 200)
        yield to_args(w, h)
