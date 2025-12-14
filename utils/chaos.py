#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.


import numpy as np

from .tqdm import trange


def runge_kutta(dt, func, **kwargs):
    def _func(z, dt=dt):
        k1 = func(z, **kwargs)
        k2 = func(z + 0.5 * dt * k1, **kwargs)
        k3 = func(z + 0.5 * dt * k2, **kwargs)
        k4 = func(z + dt * k3, **kwargs)
        z_out = z + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        return z_out

    return _func


def lorenz_func(z, a=10, b=28, c=8.0 / 3.0):
    assert z.shape[-1] == 3
    z_dot = np.zeros_like(z)
    z_dot[..., 0] = a * (z[..., 1] - z[..., 0])
    z_dot[..., 1] = z[..., 0] * (b - z[..., 2]) - z[..., 1]
    z_dot[..., 2] = z[..., 0] * z[..., 1] - c * z[..., 2]
    return z_dot


def chongxin_func(z, a=10, b=40, c=2.5, k=1, h=4):
    z_dot = np.zeros_like(z)
    z_dot[..., 0] = a * (z[..., 1] - z[..., 0])
    z_dot[..., 1] = b * z[..., 0] - k * z[..., 0] * z[..., 2]
    z_dot[..., 2] = -c * z[..., 2] + h * z[..., 0] * z[..., 0]
    return z_dot


def mackey_glass_func(gn, g0, beta: float = 0.2, gamma: float = 0.1, n: float = 10.0):
    gn_dot = beta * g0 / (1 + g0**n) - gamma * gn
    return gn_dot


def sample_mg_dynamics(
    time_steps: int,
    tau: float,
    num_split: int,
    values_before_zero=lambda t: 0.5,
    display=True,
    **kwargs,
):
    t_pre = np.linspace(-tau, 0, num_split)
    dt = t_pre[1] - t_pre[0]
    gs = [values_before_zero(t) for t in t_pre]

    out = None
    ts = np.arange(time_steps) * dt
    for idx in trange(time_steps, display=display):
        mg_func_rk4 = runge_kutta(dt, mackey_glass_func, g0=gs[0], **kwargs)
        gn = mg_func_rk4(gs[-1])
        gs = gs[1:] + [gn]
        if out is None:
            out = np.zeros((time_steps, *gs[-1].shape))
        out[idx] = gs[-1]
    return ts, out
