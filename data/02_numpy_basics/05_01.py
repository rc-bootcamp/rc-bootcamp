import random

import numpy as np

from utils.tester import to_args


def solution(arr, obs, angle):
    out = arr - obs[:, None, :]  # [t, n, 3]
    cos, sin = np.cos(angle), np.sin(angle)
    rot = cos[:, None, None, None] * np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]])
    rot += sin[:, None, None, None] * np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]])
    rot += np.array([[0, 0, 0], [0, 0, 0], [0, 0, 1]], dtype=np.float64)
    return (rot @ out[:, :, :, None])[..., 0]

    # NOTE
    # rot [t, 1, 3, 3]
    # out[..., None] [t, n, 3, 1]
    # => [t, n, 3, 1]


def dataset():
    # yield to_args(...)
    random.seed(9827419087342)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(1, 1000)
        n = random.randint(1, 100)
        arr = rnd.uniform(-10, 10, size=(t, n, 3))
        obs = rnd.uniform(-10, 10, size=(t, 3))
        angle = rnd.uniform(-np.pi, np.pi, size=(t,))
        yield to_args(arr, obs, angle)
