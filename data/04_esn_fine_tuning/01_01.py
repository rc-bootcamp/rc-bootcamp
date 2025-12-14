import random

import numpy as np

from utils.reservoir import Linear
from utils.tester import to_args


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


def solution(dim_in, dim_out, x_train, y_train, x_eval):
    # DO NOT CHANGE HERE.
    readout = BatchLRReadout(dim_in, dim_out)
    readout.train(x_train, y_train)
    return readout(x_eval)


def dataset():
    random.seed(75964382674382)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dim_in = random.randint(10, 20)
        dim_out = random.randint(1, 5)
        time_train = random.randint(50, 100)
        time_eval = random.randint(50, 100)
        ndim_x = random.randint(0, 5)
        ndim_y = random.randint(0, ndim_x)
        batch_x = [random.randint(1, 4) for _ in range(ndim_x)]
        batch_y = batch_x[len(batch_x) - ndim_y :]
        x_train = rnd.uniform(-1, 1, size=(*batch_x, time_train, dim_in))
        y_train = rnd.uniform(-1, 1, size=(*batch_y, time_train, dim_out))
        x_eval = rnd.uniform(-1, 1, size=(*batch_x, time_eval, dim_in))
        yield to_args(dim_in, dim_out, x_train, y_train, x_eval)
