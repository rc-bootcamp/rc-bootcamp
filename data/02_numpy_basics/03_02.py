import random

import numpy as np

from utils.tester import to_args


def solution(h, w, x, y, r, s, t, u, v):
    arr = np.zeros((h, w), dtype=np.uint8)
    xs, ys = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    dist = (xs - x) ** 2 + (ys - y) ** 2
    circle = dist <= r**2

    rect_x = np.logical_and(s <= xs, xs <= t)  # or (s <= xs) & (xs <= t)
    rect_y = np.logical_and(u <= ys, ys <= v)  # or (u <= ys) & (ys <= v)
    rect = np.logical_and(rect_x, rect_y)  # or rect_x & rect_y

    arr[np.logical_and(rect, circle)] = 255  # or arr[rect & circle] = ...
    arr[np.logical_xor(rect, circle)] = 127  # or arr[rect ^ circle] = ...
    return arr


def dataset():
    yield to_args(200, 200, 60, 50, 30, 10, 100, 30, 50)
    random.seed(2497328974)
    for _idx in range(99):
        h, w = [random.randint(100, 1000) for _ in range(2)]
        x = random.randint(0, h - 1)
        y = random.randint(0, w - 1)
        r = random.randint(0, min(h, w) - 1)

        s = random.randint(0, h - 2)
        t = random.randint(s + 1, h - 1)
        u = random.randint(0, w - 2)
        v = random.randint(u + 1, w - 1)
        yield to_args(h, w, x, y, r, s, t, u, v)
