import random

import numpy as np

from utils.tester import to_args


def discretize_bilinear_nplr(dt, Lambda, V, B, P, Q):
    PV = V.conj().T @ P
    QV = V.conj().T @ Q
    A0 = (2.0 / dt) * np.eye(Lambda.shape[0]) + np.diag(Lambda) - PV @ QV.conj().T
    D = np.diag(1.0 / (2.0 / dt - Lambda))
    A1 = D - ((D @ PV) * (1.0 / (1 + QV.conj().T @ D @ PV))) @ (QV.conj().T @ D)
    A_bar_nplr = A1 @ A0
    B_bar_nplr = 2 * A1 @ (V.conj().T @ B)
    return A_bar_nplr, B_bar_nplr


def solution(*args, **kwargs):
    return discretize_bilinear_nplr(*args, **kwargs)


def dataset():
    random.seed(98372498372931724)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dt = rnd.uniform(0.01, 1.0)
        Lambda = rnd.uniform(-10.0, 0.0, size=(random.randint(1, 128), 2))
        Lambda = Lambda[:, 0] + 1j * Lambda[:, 1]
        L = Lambda.shape[0]
        V_real = rnd.normal(0.0, 1.0, size=(L, L))
        V_imag = rnd.normal(0.0, 1.0, size=(L, L))
        V = V_real + 1j * V_imag
        B = rnd.normal(0.0, 1.0, size=(L, 1))
        P = rnd.normal(0.0, 1.0, size=(L, 1))
        Q = rnd.normal(0.0, 1.0, size=(L, 1))
        yield to_args(dt, Lambda, V, B, P, Q)
