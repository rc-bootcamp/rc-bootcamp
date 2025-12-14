import random

import numpy as np
import scipy.optimize

from utils.reservoir import Linear
from utils.tester import to_args


def calc_df_and_lambda(xs: np.array, df_max: int = None, num_cand: int = None, lmbd0=1e-12):
    batch_size, dim = xs.shape[:-2], xs.shape[-1]
    if df_max is None:
        df_max = dim
    if num_cand is None:
        num_cand = df_max

    _left, sigma, _right = np.linalg.svd(xs)
    sigma2 = (sigma**2)[..., None, :]  # [*bs, 1, dim]
    dfs = np.linspace(0, df_max, num_cand + 1)[1:]  # candidates
    init_cond = np.full((*batch_size, num_cand), lmbd0)  # initial condition for λ -> [*bs, num_cand]

    def func(lmbd):
        # lmbd: [*bs, num_cand], sigma2: [*bs, 1, dim]
        return dfs - np.sum(sigma2 / (lmbd[..., None] + sigma2), axis=-1)

    def fprime(lmbd):
        # lmbd: [*bs, num_cand], sigma2: [*bs, 1, dim]
        return np.sum(sigma2 / (lmbd[..., None] + sigma2) ** 2, axis=-1)

    lmbds = scipy.optimize.newton(func, init_cond, fprime)  # solve f(λ) = 0 with f' -> [*bs, num_cand]
    lmbds[lmbds < 0] = 0  # remove negative λ
    return dfs, lmbds


def calc_aic(xs, ys, **kwargs):
    assert xs.shape[-2] == ys.shape[-2]
    *batch_size, length, dim_in = xs.shape
    dfs, lmbds = calc_df_and_lambda(xs, **kwargs)  # [num_cand], [*bs, num_cand]
    xs = xs[..., None, :, :]  # [*bs, 1, length, dim_in]
    ys = ys[..., None, :, :]  # [*bs, 1, length, dim_in]
    xtx = xs.swapaxes(-2, -1) @ xs  # [*bs, 1, dim_in, dim_in]
    xty = xs.swapaxes(-2, -1) @ ys  # [*bs, 1, dim_in, dim_out]
    sol = np.matmul(
        np.linalg.pinv(xtx + lmbds[..., None, None] * np.eye(dim_in)), xty
    )  # [*bs, num_cand, dim_in, dim_out]
    rss = np.square(xs @ sol - ys).sum(axis=(-2, -1))  # [*bs, num_cand]
    aics = length * np.log(rss) + dfs  # [*bs, num_cand]
    return dfs, lmbds, sol, rss, aics


class AutoRidgeReadout(Linear):
    def __init__(self, *args, lmbd: float = 0.0, **kwargs):
        super(AutoRidgeReadout, self).__init__(*args, **kwargs)
        self.lmbd = lmbd

    def train(self, x: np.ndarray, y: np.ndarray, **kwargs):
        assert (x.ndim > 1) and (x.shape[-1] == self.input_dim)
        assert (y.ndim > 1) and (y.shape[-1] == self.output_dim)
        x_biased = np.ones((*x.shape[:-1], x.shape[-1] + 1), dtype=self.dtype)
        x_biased[..., 1:] = x
        dfs, lmbds, sol, rss, aics = calc_aic(x_biased, y, **kwargs)
        # dfs: [num_cand], lmbds: [*bs, num_cand]
        # sol: [*bs, num_cand, dim_in, dim_out]
        # rss: [*bs, num_cand], aics: [*bs, num_cand]
        best_idx = np.argmin(aics, axis=-1)
        sol_best = sol[(*np.indices(best_idx.shape), best_idx)]
        self.lmbd = lmbds[(*np.indices(best_idx.shape), best_idx)]
        self.weight = sol_best[..., 1:, :].swapaxes(-2, -1)
        self.bias = sol_best[..., :1, :]
        return self.weight, self.bias, dfs, lmbds, sol, rss, aics


def solution(dim_in, dim_out, x_train, y_train, x_eval):
    # DO NOT CHANGE HERE.
    readout = AutoRidgeReadout(dim_in, dim_out)
    readout.train(x_train, y_train)
    return readout(x_eval)


def dataset():
    random.seed(43954783982131)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dim_in = random.randint(10, 20)
        dim_out = random.randint(1, 5)
        time_train = random.randint(50, 100)
        time_eval = random.randint(50, 100)
        ndim_x = random.randint(0, 2)
        ndim_y = random.randint(0, ndim_x)
        batch_x = [random.randint(1, 5) for _ in range(ndim_x)]
        batch_y = batch_x[len(batch_x) - ndim_y :]
        x_train = rnd.uniform(-1, 1, size=(*batch_x, time_train, dim_in))
        y_train = rnd.uniform(-1, 1, size=(*batch_y, time_train, dim_out))
        x_eval = rnd.uniform(-1, 1, size=(*batch_x, time_eval, dim_in))
        yield to_args(dim_in, dim_out, x_train, y_train, x_eval)
