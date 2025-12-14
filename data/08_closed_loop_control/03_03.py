import random

import numpy as np

from utils.reservoir import ESN, Linear
from utils.tester import to_args
from utils.tqdm import trange


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


def emulate_parallel(
    time_steps,
    x0,
    net,
    w_feed,
    w_in,
    w_out,
    ds=None,
    us=None,
    train_range=None,
    force_every=1,
    display=True,
):
    train_range = [0, 0] if train_range is None else train_range
    record = {}
    record["t"] = np.arange(0, time_steps + 1)
    record["x"] = np.zeros((time_steps + 1, *x0.shape))
    record["y"] = np.zeros((time_steps, *w_out(x0).shape))
    record["d"] = np.zeros((time_steps, *w_out(x0).shape))
    record["w"] = np.zeros((time_steps + 1, *w_out.weight.shape))
    record["train_range"] = train_range

    x = x0
    record["x"][0] = x0
    record["w"][0] = w_out.weight
    pbar = trange(time_steps, display=display)
    for idx in pbar:
        y = w_out(x)
        d = ds[idx] if (ds is not None) and (idx < len(ds)) else 0.0
        u = us[idx] if (us is not None) and (idx < len(us)) else 0.0
        if idx % force_every == 0 and (train_range[0] <= idx < train_range[1]):
            if x.ndim == 1:
                dws = w_out.step(x, d)
            elif x.ndim == 2:
                dws = []
                for idy in range(x.shape[0]):
                    out = w_out.step(x[idy], d[idy])
                    dws.append(out)
            pbar.set_description("|ΔW|={:.3e}".format(np.linalg.norm(dws)))
        x = net(x, w_feed(y) + w_in(u))  # x(t + 1) = f(x(t), ...)
        record["x"][idx + 1] = x
        record["y"][idx] = y
        record["d"][idx] = d
        record["w"][idx + 1] = w_out.weight
    return record


def solution(time_steps, x0, net, w_feed, w_in, dim, dim_in, **kwargs):
    w_out = FORCEReadout(dim, dim_in)
    record = emulate_parallel(time_steps, x0, net, w_feed, w_in, w_out, **kwargs)
    return record["x"], record["y"]


def dataset():
    random.seed(897943827432)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        time_steps = 100
        dim = random.randint(10, 20)
        dim2 = random.randint(1, 3)
        x0 = rnd.uniform(-1, 1, (dim2, dim))
        dim_in = random.randint(1, 5)
        sr = random.uniform(0, 1)
        net = ESN(dim, sr=sr, rnd=rnd)
        w_feed = Linear(dim_in, dim, rnd=rnd)
        w_in = Linear(1, dim, rnd=rnd)
        ds = rnd.uniform(-1, 1, (time_steps, dim2, dim_in))
        us = rnd.uniform(-1, 1, (time_steps, 1))
        yield to_args(
            time_steps,
            x0,
            net,
            w_feed,
            w_in,
            dim,
            dim_in,
            ds=ds,
            us=us,
            train_range=[25, 75],
            display=False,
        )
