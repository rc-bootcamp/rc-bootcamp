import random

import numpy as np

from utils.chaos import runge_kutta
from utils.tester import to_args
from utils.tqdm import trange


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
            out = np.zeros((time_steps, *gn.shape))
        out[idx] = gn
    return ts, out


def solution(*args, **kwargs):
    return sample_mg_dynamics(*args, **kwargs)


def dataset():
    random.seed(7864893726894732)
    # rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        tau = random.uniform(15, 20)
        num_split = random.randint(10, 100)
        history = random.uniform(0, 1)
        yield to_args(100, tau, num_split, lambda t: history, display=False)  # noqa: B023
