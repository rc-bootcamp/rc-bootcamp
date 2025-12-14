import random

import numpy as np

from utils.tester import to_args


def solution(h, w, x, y, r):
    arr = np.zeros((h, w), dtype=np.uint8)
    xs, ys = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    dist = (xs - x) ** 2 + (ys - y) ** 2

    # Alternative solution for `dist`.
    # dist = (np.arange(h)[:, None] - x)**2 + (np.arange(w)[None, :] - y)**2

    circle = dist <= r**2
    arr[circle] = 255
    return arr


def dataset():
    yield to_args(200, 200, 40, 50, 30)
    random.seed(726734826739)
    for _idx in range(99):
        h, w = [random.randint(100, 1000) for _ in range(2)]
        x = random.randint(0, h - 1)
        y = random.randint(0, w - 1)
        r = random.randint(0, min(h, w) - 1)
        yield to_args(h, w, x, y, r)
