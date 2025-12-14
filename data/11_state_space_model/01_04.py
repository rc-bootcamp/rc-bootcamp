import random

import numpy as np
import scipy

from utils.tester import to_args


def discretize_zoh(dt, A, B):
    A_bar = scipy.linalg.expm(A * dt)
    B_bar = scipy.linalg.lstsq(A * dt, (A_bar - np.eye(A.shape[0])) @ (B * dt))[0]
    return A_bar, B_bar


def discretize_bilinear(dt, A, B):
    eye = np.eye(A.shape[0])
    A_bar = scipy.linalg.lstsq(eye - A * dt / 2, eye + A * dt / 2)[0]
    B_bar = scipy.linalg.lstsq(eye - A * dt / 2, B * dt)[0]
    return A_bar, B_bar


def discretize(dt, A, B, method="zoh"):
    # DO NOT CHANGE HERE.
    if method == "zoh":
        return discretize_zoh(dt, A, B)
    elif method == "bilinear":
        return discretize_bilinear(dt, A, B)
    else:
        raise ValueError(f"Unknown method: {method}")


def solution(dt, A, B):
    # DO NOT CHANGE HERE.
    A_bar_zoh, B_bar_zoh = discretize(dt, A, B, method="zoh")
    A_bar_bil, B_bar_bil = discretize(dt, A, B, method="bilinear")
    return A_bar_zoh, B_bar_zoh, A_bar_bil, B_bar_bil


def transition_leg_t(N, theta=1.0):
    arange = np.arange(N)
    base = (2 * arange + 1) ** 0.5
    diff = arange[:, None] - arange[None, :]
    A = base[:, None] * base[None, :]
    A[(diff >= 0) | (diff % 2 == 0)] *= -1
    B = np.array(base)[:, None]
    A /= float(theta)
    B /= float(theta)
    return A, B


def dataset():
    random.seed(849712363123632)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        dt = rnd.uniform(0.01, 1.0)
        theta = rnd.uniform(dt * 2, 10.0)
        N = random.randint(2, 128)
        A, B = transition_leg_t(N, theta)
        yield to_args(dt, A, B)
