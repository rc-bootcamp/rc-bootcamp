import random

import numpy as np

from utils.reservoir import ESN, Linear
from utils.tester import to_args
from utils.tqdm import trange


def emulate_offline(time_steps, x0, net, w_feed, w_out, ds=None, open_range=None, label=None, display=True):
    open_range = [0, 0] if open_range is None else open_range
    record = {}
    record["t"] = np.arange(0, time_steps + 1)
    record["x"] = np.zeros((time_steps + 1, *x0.shape))
    record["y"] = np.zeros((time_steps, *w_out(x0).shape))
    record["open_range"] = open_range

    x = x0
    record["x"][0] = x0
    pbar = trange(time_steps, display=display)
    for idx in pbar:
        if label is not None:
            pbar.set_description(label)
        if (ds is not None) and (idx < len(ds)) and (open_range[0] <= idx < open_range[1]):
            y = ds[idx]
        else:
            y = w_out(x)
        x = net(x, w_feed(y))
        record["x"][idx + 1] = x
        record["y"][idx] = y
    return record


def solution(*args, **kwargs):
    record = emulate_offline(*args, **kwargs)
    return record["x"], record["y"]


def dataset():
    random.seed(329473832974329)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        time_steps = 100
        dim = random.randint(10, 20)
        x0 = rnd.uniform(-1, 1, dim)
        dim_in = random.randint(1, 5)
        sr = random.uniform(0, 1)
        net = ESN(dim, sr=sr, rnd=rnd)
        w_out = Linear(dim, dim_in, rnd=rnd)
        w_feed = Linear(dim_in, dim, rnd=rnd)
        ds = rnd.uniform(-1, 1, (time_steps, dim_in))
        yield to_args(time_steps, x0, net, w_feed, w_out, ds=ds, open_range=[0, 50], display=False)
