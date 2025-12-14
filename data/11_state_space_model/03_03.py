import random

import numpy as np

from ipc_module.polynomial import Legendre
from utils.tester import to_args


def basis_leg_s(N, S, tau=1.0):
    basis = np.zeros((N, len(S)))
    non_zero = S <= 0
    poly = Legendre(2 * np.exp(S[non_zero] / tau) - 1)
    for idx in range(N):
        basis[idx, non_zero] = poly[idx]  # Evaluate the n-th order polynomial
    basis[:, non_zero] *= ((2 * np.arange(N) + 1) ** 0.5)[:, None]
    return basis


def solution(*args, **kwargs):
    return basis_leg_s(*args, **kwargs)


def dataset():
    random.seed(498732234281113247)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        N = random.randint(1, 128)
        S = rnd.uniform(-20.0, 20.0, size=(100,))
        tau = rnd.uniform(0.1, 10.0)
        yield to_args(N, S, tau)
