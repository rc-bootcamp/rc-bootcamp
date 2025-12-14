import math
import random

import numpy as np

from utils.tester import to_args


def transition_fou_t(N, theta=1.0):
    A = np.zeros((N, N))
    A[0, 0] = -2
    A[0, 2::2] = -2 * math.sqrt(2)
    A[2::2, 0] = -2 * math.sqrt(2)
    A[2::2, 2::2] = -4
    diag = 2 * np.pi * (np.arange(N - 1) // 2)
    diag[1::2] = 0
    A += np.diag(diag, -1) - np.diag(diag, 1)
    B = -A[:, :1] / theta
    A = A / theta
    return A, B


def solution(*args, **kwargs):
    return transition_fou_t(*args, **kwargs)


def dataset():
    random.seed(123421321)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        N = random.randint(1, 128)
        theta = rnd.uniform(0.1, 10.0)
        yield to_args(N, theta)
