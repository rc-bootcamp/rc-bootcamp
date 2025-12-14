import random

import numpy as np

from utils.reservoir import ESN
from utils.tester import to_args
from utils.tqdm import trange


def calc_max_lyapunov_exponent(func, x0, T, eps=1e-6, pert=None, display=False):
    if pert is None:
        pert = np.ones_like(x0)
    *batch_size, dim = x0.shape
    pert /= np.linalg.norm(pert, axis=-1, keepdims=True)
    lmbds = np.zeros((*batch_size, T))
    x_pre, x_post = x0, x0 + eps * pert
    x = np.stack([x_pre, x_post])
    for idx in trange(T, display=display):
        x = func(x, idx)
        x_pre, x_post = x[0], x[1]
        x_diff = x_post - x_pre
        d_post = np.linalg.norm(x_diff, axis=-1, keepdims=True)
        lmbd = np.log(np.abs(d_post / eps))
        x_post[:] = x_pre + x_diff * (eps / d_post)
        lmbds[..., idx] = lmbd[..., 0]
    exponent = np.mean(lmbds, axis=-1)
    return lmbds, exponent


def solution(*args, **kwargs):
    return calc_max_lyapunov_exponent(*args, **kwargs)


def dataset():
    random.seed(9568342)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(10):
        dim = random.randint(10, 100)
        sr = random.uniform(1.0, 1.5)
        net = ESN(dim=dim, sr=sr, rnd=rnd)
        x0 = rnd.uniform(-1, 1, size=dim)
        T = rnd.integers(10, 100)
        pert = rnd.normal(size=dim)
        yield to_args(lambda x, _idx, net=net: net(x), x0, T, pert=pert)
