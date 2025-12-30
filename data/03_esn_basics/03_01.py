import random

import numpy as np

from utils.reservoir import Linear
from utils.tester import to_args


class LRReadout(Linear):
    def train(self, x: np.ndarray, y: np.ndarray):
        assert (x.ndim == 2) and (x.shape[-1] == self.input_dim)
        assert (y.ndim == 2) and (y.shape[-1] == self.output_dim)
        x_biased = np.ones((x.shape[0], x.shape[1] + 1), dtype=self.dtype)
        x_biased[:, 1:] = x
        sol, _residuals, _rank, _s = np.linalg.lstsq(x_biased, y, rcond=None)
        self.weight[:] = sol[1:].T
        self.bias[:] = sol[0]
        return self.weight, self.bias


def solution(dim_in, dim_out, x_train, y_train, x_eval):
    # DO NOT CHANGE HERE.
    readout = LRReadout(dim_in, dim_out)
    readout.train(x_train, y_train)
    return readout(x_eval)


def dataset():
    random.seed(34218973452)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dim_in = random.randint(20, 50)
        dim_out = random.randint(1, 5)
        time_step = random.randint(100, 1000)
        x_train = rnd.uniform(-1, 1, size=(time_step, dim_in))
        y_train = rnd.uniform(-1, 1, size=(time_step, dim_out))
        x_eval = rnd.uniform(-1, 1, size=(time_step, dim_in))
        yield to_args(dim_in, dim_out, x_train, y_train, x_eval)
