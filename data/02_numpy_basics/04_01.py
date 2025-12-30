import random

import numpy as np

from utils.tester import to_args


def solution(arr):
    out = np.zeros_like(arr)
    sq = (arr**2).cumsum(axis=2) ** 0.5
    r_xy = sq[..., 1]
    r_xyz = sq[..., 2]

    # Alternative solution.
    # r_xy = np.linalg.norm(arr[..., :2], axis=-1)
    # r_xyz = np.linalg.norm(arr, axis=-1)

    th = np.arccos(arr[..., 2] / r_xyz)
    ph = np.sign(arr[..., 1]) * np.arccos(arr[..., 0] / r_xy)
    out[..., 0] = r_xyz
    out[..., 1] = th
    out[..., 2] = ph
    return out


def dataset():
    random.seed(43278463278123)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(100, 1000)
        n = random.randint(1, 100)
        r = rnd.uniform(1.0, 10, size=(t, n))
        th = rnd.uniform(0, np.pi, size=(t, n))
        ph = rnd.uniform(-np.pi, np.pi, size=(t, n))
        arg = np.zeros((t, n, 3))
        arg[..., 0] = r * np.sin(th) * np.cos(ph)
        arg[..., 1] = r * np.sin(th) * np.sin(ph)
        arg[..., 2] = r * np.cos(th)
        yield to_args(arg)
