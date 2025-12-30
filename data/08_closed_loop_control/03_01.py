import random

import numpy as np

from utils.reservoir import Linear
from utils.tester import to_args


def rls_update(P, x):
    k = np.dot(P, x)
    g = 1 / (1 + x.dot(k))
    dP = g * np.outer(k, k)
    P_new = P - dP
    return g, k, P_new


class FORCEReadout(Linear):
    def __init__(self, *args, lmbd=1.0, initialize_with_zero=True, **kwargs):
        super(FORCEReadout, self).__init__(*args, **kwargs)
        self.P = np.eye(self.input_dim, dtype=self.dtype) * (1 / lmbd)
        if initialize_with_zero:
            self.weight[:] = 0
            self.bias[:] = 0

    def step(self, x, d):
        assert x.ndim == 1
        e = d - self(x)
        dw = np.zeros_like(self.weight)
        g, k, P_new = rls_update(self.P, x)
        dw = g * np.outer(e, k)
        self.P = P_new
        self.weight += dw
        return dw


def solution(dim_in, dim_out, x_train, y_train, x_eval):
    # DO NOT CHANGE HERE.
    readout = FORCEReadout(dim_in, dim_out)
    readout.step(x_train, y_train)
    return readout(x_eval)


def dataset():
    random.seed(896742789438926)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        dim_in = random.randint(20, 50)
        dim_out = random.randint(1, 5)
        x_train = rnd.uniform(-1, 1, size=(dim_in,))
        y_train = rnd.uniform(-1, 1, size=(dim_out,))
        x_eval = rnd.uniform(-1, 1, size=(dim_in,))
        yield to_args(dim_in, dim_out, x_train, y_train, x_eval)
