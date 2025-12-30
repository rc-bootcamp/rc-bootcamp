import math
import random

import numpy as np

from utils.tester import to_args


def measure_fou_t(S, theta=1.0):
    measure = np.where((-theta <= S) & (S <= 0), 1.0 / theta, 0.0)
    return measure


def basis_fou_t(N, S, theta=1.0):
    basis = np.zeros((N, len(S)))
    non_zero = (-theta <= S) & (S <= 0)
    basis[0, non_zero] = 1
    basis[1::2, non_zero] = -math.sqrt(2) * np.sin((np.arange(0, N - 1, 2)[:, None] * np.pi * S[non_zero] / theta))
    basis[2::2, non_zero] = math.sqrt(2) * np.cos((np.arange(2, N, 2)[:, None] * np.pi * S[non_zero] / theta))
    return basis


def solution(N, S, theta=1.0):
    # DO NOT CHANGE HERE.
    measure = measure_fou_t(S, theta=theta)
    basis = basis_fou_t(N, S, theta=theta)
    return measure, basis


def dataset():
    random.seed(979187239624921)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        S = rnd.uniform(-2.0, 2.0, size=random.randint(10, 1000))
        N = random.randint(1, 128)
        theta = rnd.uniform(0.1, 10.0)
        yield to_args(N, S, theta)
