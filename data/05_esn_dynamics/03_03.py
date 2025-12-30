import random

import numpy as np

from utils.reservoir import ESN
from utils.tester import to_args


def calc_jacobian(net, xs):
    assert net.f == np.tanh
    ys = net.sr * np.square(1 / np.cosh(net.sr * np.matmul(xs, net.weight.swapaxes(-1, -2))))
    js = net.weight * ys[..., :, None]
    if net.a is None:
        return js
    else:
        return (1 - net.a) * np.eye(net.dim) + net.a * js


def solution(*args, **kwargs):
    return calc_jacobian(*args, **kwargs)


def dataset():
    random.seed(89732498)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(10):
        dim = random.randint(10, 100)
        a = random.uniform(0.1, 0.9)
        sr = random.uniform(0.5, 1.5)
        net = ESN(dim=dim, sr=sr, a=a, rnd=rnd)
        t = random.randint(1, 100)
        x = rnd.uniform(-1, 1, size=(t, dim))
        yield to_args(net, x)
    for _idx in range(10):
        dim = random.randint(10, 100)
        sr = random.uniform(0.5, 1.5)
        net = ESN(dim=dim, sr=sr, rnd=rnd)
        t = random.randint(1, 100)
        x = rnd.uniform(-1, 1, size=(t, dim))
        yield to_args(net, x)
