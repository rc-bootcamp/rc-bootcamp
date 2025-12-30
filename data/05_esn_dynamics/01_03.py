import random

import numpy as np

from utils.tester import to_args


def lorenz_func(z, a=10, b=28, c=8.0 / 3.0):
    assert z.shape[-1] == 3
    z_dot = np.zeros_like(z)
    z_dot[..., 0] = a * (z[..., 1] - z[..., 0])
    z_dot[..., 1] = z[..., 0] * (b - z[..., 2]) - z[..., 1]
    z_dot[..., 2] = z[..., 0] * z[..., 1] - c * z[..., 2]
    return z_dot


def runge_kutta(dt, func, **kwargs):
    def _func(z, dt=dt):
        k1 = func(z, **kwargs)
        k2 = func(z + 0.5 * dt * k1, **kwargs)
        k3 = func(z + 0.5 * dt * k2, **kwargs)
        k4 = func(z + dt * k3, **kwargs)
        z_out = z + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        return z_out

    return _func


def solution(dt, func, z, **kwargs):
    func = runge_kutta(dt, func, **kwargs)
    return func(z)


def dataset():
    random.seed(23470955098)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dt = random.uniform(0, 1)
        n = random.randint(1, 100)
        z = rnd.standard_normal(size=(n, 3))
        yield to_args(dt, lorenz_func, z)
