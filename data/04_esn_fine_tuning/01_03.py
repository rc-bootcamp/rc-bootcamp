import random

import numpy as np

from utils.reservoir import ESN, Linear
from utils.task import narma_func
from utils.tester import to_args
from utils.tqdm import trange


class BatchLRReadout(Linear):
    def train(self, x: np.ndarray, y: np.ndarray):
        assert (x.ndim > 1) and (x.shape[-1] == self.input_dim)
        assert (y.ndim > 1) and (y.shape[-1] == self.output_dim)
        x_biased = np.ones((*x.shape[:-1], x.shape[-1] + 1), dtype=self.dtype)
        x_biased[..., 1:] = x
        sol = np.matmul(np.linalg.pinv(x_biased), y)
        self.weight = sol[..., 1:, :].swapaxes(-2, -1)
        self.bias = sol[..., :1, :]
        return self.weight, self.bias


def calc_batch_nrmse(y, yhat):
    mse = y - yhat
    mse = (mse * mse).mean(axis=-2)
    var = y.var(axis=-2)
    return (mse / var) ** 0.5


def create_setup(seed, dim, rho, a=None, f=np.tanh, bound=1.0, bias=0.0, cls=BatchLRReadout):
    rnd = np.random.default_rng(seed)
    w_in = Linear(1, dim, bound=bound, bias=bias, rnd=rnd)
    net = ESN(dim, sr=rho, f=f, a=a, rnd=rnd)
    w_out = cls(dim, 1)
    return w_in, net, w_out


def sample_dataset(
    seed,
    t_washout=1000,
    t_train=2000,
    t_eval=1000,
    narma_parameters=None,
):
    narma_parameters = (
        dict(alpha=0.3, beta=0.05, gamma=1.5, delta=0.1, mu=0.25, kappa=0.25)
        if narma_parameters is None
        else narma_parameters
    )
    rnd = np.random.default_rng(seed)
    t_total = t_washout + t_train + t_eval
    ts = np.arange(-t_washout, t_train + t_eval)
    us = rnd.uniform(-1, 1, (t_total, 1))
    ys = narma_func(us, np.zeros((10, 1)), **narma_parameters)
    time_info = dict(t_washout=t_washout, t_train=t_train, t_eval=t_eval)
    return ts, us, ys, time_info


def sample_dynamics(x0, w_in, net, ts, vs, display=False):
    assert vs.shape[-2] == ts.shape[0]
    x = x0
    xs = np.zeros((*x.shape[:-1], ts.shape[0], x.shape[-1]))
    for idx in trange(ts.shape[0], display=display):
        x = net(x, w_in(vs[..., idx, :]))
        xs[..., idx, :] = x
    return xs


def eval_nrmse(xs, ys, w_out, time_info, return_out=False, **kwargs):
    t_washout, t_eval = time_info["t_washout"], time_info["t_eval"]
    x_train, y_train = xs[..., t_washout:-t_eval, :], ys[..., t_washout:-t_eval, :]
    x_eval, y_eval = xs[..., -t_eval:, :], ys[..., -t_eval:, :]
    out = w_out.train(x_train, y_train, **kwargs)
    y_out = w_out(x_eval)
    nrmse = calc_batch_nrmse(y_eval, y_out)
    if return_out:
        return nrmse, *out
    else:
        return nrmse


def train_and_eval(x0, w_in, net, w_out, ts, vs, ys, time_info, display=False):
    assert vs.shape[-2] == ts.shape[0]
    assert ys.shape[-2] == ts.shape[0]
    xs = sample_dynamics(x0, w_in, net, ts, vs, display=display)
    nrmse = eval_nrmse(xs, ys, w_out, time_info)
    return nrmse, xs


def solution(*args, **kwargs):
    return train_and_eval(*args, **kwargs)


def dataset():
    random.seed(54839754938)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(10):
        seed1 = random.randint(1, 10000)
        seed2 = random.randint(1, 10000)
        dim = random.randint(10, 50)
        w_in, net, w_out = create_setup(seed1, dim, 0.9)
        ndim = random.randint(0, 2)
        batch_size = [random.randint(1, 2) for _ in range(ndim)]
        ts, us, ys, time_info = sample_dataset(seed2, t_washout=100, t_train=100, t_eval=100)
        x0 = rnd.uniform(-1, 1, (*batch_size, dim))
        yield to_args(x0, w_in, net, w_out, ts, us, ys, time_info)
