import math
import random

import numpy as np

from utils.tester import to_args


class Module(object):
    def __init__(self, *_args, seed=None, rnd=None, dtype=np.float64, **_kwargs):
        if rnd is None:
            self.rnd = np.random.default_rng(seed)
        else:
            self.rnd = rnd
        self.dtype = dtype


class Linear(Module):
    def __init__(self, input_dim: int, output_dim: int, bound: float = None, bias: float = 0.0, **kwargs):
        """
        Linear model

        Args:
            input_dim (int): input node dim.
            output_dim (int): output node dim.
        """
        super(Linear, self).__init__(**kwargs)
        self.input_dim = input_dim
        self.output_dim = output_dim
        if bound is None:
            bound = math.sqrt(1 / input_dim)
        self.weight = self.rnd.uniform(-bound, bound, (output_dim, input_dim)).astype(self.dtype)
        self.bias = self.rnd.uniform(-bias, bias, (output_dim,)).astype(self.dtype)

    def __call__(self, x: np.ndarray):
        x = np.asarray(x)
        out = np.matmul(x, self.weight.swapaxes(-1, -2)) + self.bias
        return out


def solution(input_dim, output_dim, seed, bound, bias, mat):
    # DO NOT CHANGE HERE.
    lin = Linear(input_dim, output_dim, bound=bound, bias=bias, seed=seed)
    return lin(mat)


def dataset():
    random.seed(832907432432)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        input_dim = random.randint(1, 100)
        output_dim = random.randint(1, 100)
        ndim = random.randint(0, 5)
        seed = random.randint(0, 10000)
        mat_shape = [random.randint(1, 3) for _ in range(ndim)] + [input_dim]
        bound, bias = 1.0, 1.0
        mat = rnd.uniform(-100, 100, size=mat_shape)
        yield to_args(input_dim, output_dim, seed, bound, bias, mat)
