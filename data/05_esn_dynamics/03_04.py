import random

import numpy as np

from utils.reservoir import ESN
from utils.tester import to_args
from utils.tqdm import trange


def calc_jacobian(net, xs):
    assert net.f == np.tanh
    ys = net.sr * np.square(1 / np.cosh(net.sr * np.matmul(xs, net.weight.swapaxes(-1, -2))))
    js = net.weight * ys[..., :, None]
    if net.a is None:
        return js
    else:
        return (1 - net.a) * np.eye(net.dim) + net.a * js


def calc_lyapunov_exponents(net, xs, display=False):
    length, *bs, dim = xs.shape
    rs = np.zeros_like(xs)
    js = calc_jacobian(net, xs)
    q_pre = np.zeros((*bs, dim, dim))
    q_pre[..., :, :] = np.eye(dim)
    for idx in trange(length, display=display):
        q, r = np.linalg.qr(np.matmul(js[idx], q_pre))
        rs[idx] = np.diagonal(r, axis1=-2, axis2=-1)
        q_pre = q
    lyaps = np.log(np.abs(rs)).mean(axis=0)
    return lyaps


def solution(*args, **kwargs):
    return calc_lyapunov_exponents(*args, **kwargs)


def dataset():
    random.seed(89732498)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(10):
        dim = random.randint(10, 100)
        sr = random.uniform(0.5, 1.5)
        net = ESN(dim=dim, sr=sr, rnd=rnd)
        t = random.randint(1, 100)
        x = rnd.uniform(-1, 1, size=(t, dim))
        yield to_args(net, x)
