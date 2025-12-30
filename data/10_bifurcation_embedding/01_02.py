import random

import numpy as np

from utils.reservoir import ESN, Linear, RidgeReadout
from utils.tester import to_args
from utils.tqdm import trange


def emulate_with_controll(
    time_steps,
    x0,
    net,
    w_feed,
    w_param,
    w_out,
    us,
    ds=None,
    open_range=None,
    label=None,
    display=True,
    save_x=True,
):
    open_range = open_range if open_range is not None else [0, 0]
    record = {}
    record["t"] = np.arange(0, time_steps + 1)
    record["y"] = np.zeros((time_steps, *w_out(x0).shape))
    record["open_range"] = open_range
    x = x0
    if save_x:
        record["x"] = np.zeros((time_steps + 1, *x0.shape))
        record["x"][0] = x0
    pbar = trange(time_steps, display=display)
    for idx in pbar:
        if label is not None:
            pbar.set_description(label)
        if (ds is not None) and (idx < len(ds)) and (open_range[0] <= idx < open_range[1]):
            y = ds[idx]  # training phase (i.e., teacher forcing by ds)
        else:
            y = w_out(x)  # evaluation phase (i.e., autonomous closed-loop mode by w_out)
        u = us[idx]  # x(t + 1) = f(x(t), y(t), u(t))
        x = net(x, w_feed(y) + w_param(u))
        record["y"][idx] = y
        if save_x:
            record["x"][idx + 1] = x
    return record


def run_train_and_eval(t_washout, t_train, t_eval, x0, net, w_feed, w_param, w_out, us, ds, display=True):
    # training phase (open loop)
    record_t = emulate_with_controll(
        t_washout + t_train,
        x0,
        net,
        w_feed,
        w_param,
        w_out,
        us,
        ds,
        open_range=[0, t_washout + t_train],
        label="Train",
        display=display,
    )

    # run ridge_regression and update the weight
    x_train = record_t["x"][t_washout : t_washout + t_train]  # t \in [t_washout, t_washout + t_train)
    y_train = record_t["y"][t_washout : t_washout + t_train]  # t \in [t_washout, t_washout + t_train)
    y_eval = ds[t_washout + t_train : t_washout + t_train + t_eval]

    # train w_out with x_train and y_train
    w_out.train(
        x_train.reshape(-1, w_out.input_dim),
        y_train.reshape(-1, w_out.output_dim),
    )

    # evaluation phase (closed loop)
    x1 = np.array(record_t["x"][-1])
    record_e = emulate_with_controll(t_eval, x1, net, w_feed, w_param, w_out, us=us, label="Eval", display=display)
    record_e["d"] = y_eval
    return record_t, record_e


def solution(*args, **kwargs):
    _record_t, record_e = run_train_and_eval(*args, **kwargs)
    return record_e["x"], record_e["y"]


def dataset():
    random.seed(329473832974329)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        time_steps = 100, 100, 100
        dim = random.randint(10, 20)
        x0 = rnd.uniform(-1, 1, dim)
        dim_in = random.randint(1, 5)
        dim_param = random.randint(1, 5)
        sr = random.uniform(0, 1)
        net = ESN(dim, sr=sr, rnd=rnd)
        w_out = RidgeReadout(dim, dim_in, rnd=rnd)
        w_feed = Linear(dim_in, dim, rnd=rnd)
        w_param = Linear(dim_param, dim, rnd=rnd)
        ds = rnd.uniform(-1, 1, (sum(time_steps), dim_in))
        cs = rnd.uniform(-1, 1, (sum(time_steps), dim_param))
        yield to_args(*time_steps, x0, net, w_feed, w_param, w_out, cs, ds, display=False)
