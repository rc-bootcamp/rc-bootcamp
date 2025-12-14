import random

import numpy as np
from scipy.sparse.linalg import ArpackNoConvergence, eigs

from utils.reservoir import Module
from utils.tester import to_args


class ESN(Module):
    def __init__(
        self,
        dim: int,
        sr: float = 1.0,
        f=np.tanh,
        a: float | None = None,
        p: float = 1.0,
        init_state: np.ndarray | None = None,
        normalize: bool = True,
        **kwargs,
    ):
        """
        Echo state network [Jaeger, H. (2001). Bonn, Germany:
        German National Research Center for Information Technology GMD Technical Report, 148(34), 13.]

        Args:
            dim (int): number of the ESN nodes
            sr (float, optional): spectral radius. Defaults to 1.0.
            f (callable, optional): activation function. Defaults to np.tanh.
            a (float | None, optional): leaky rate. Defaults to None.
            p (float, optional): density of connection matrix. Defaults to 1.0.
            init_state (np.ndarray | None, optional): initial states. Defaults to None.
            normalize (bool, optional): decide if normalizing connection matrix. Defaults to True.
        """
        super(ESN, self).__init__(**kwargs)
        self.dim = dim
        self.sr = sr
        self.f = f
        self.a = a
        self.p = p
        if init_state is None:
            self.x_init = np.zeros(dim, dtype=self.dtype)
        else:
            self.x_init = np.array(init_state, dtype=self.dtype)
        self.x = np.array(self.x_init)
        # generating normalzied sparse matrix
        while True:
            try:
                self.weight = self.rnd.normal(size=(self.dim, self.dim)).astype(self.dtype)
                if self.p < 1.0:
                    w_con = np.full((dim * dim,), False)
                    w_con[: int(dim * dim * self.p)] = True
                    w_con = w_con.reshape((dim, dim))
                    self.rnd.shuffle(w_con)
                    self.weight = self.weight * w_con
                if normalize:
                    eigen_values = eigs(self.weight, return_eigenvectors=False, k=1, which="LM", v0=np.ones(self.dim))
                    spectral_radius = max(abs(eigen_values))
                    self.weight = self.weight / spectral_radius
                break
            except ArpackNoConvergence:
                continue

    def __call__(self, x: np.ndarray, v: np.ndarray | None = None):
        x_next = self.sr * np.matmul(x, self.weight.swapaxes(-1, -2))
        if v is not None:
            x_next += v
        x_next = self.f(x_next)
        if self.a is None:
            return x_next
        else:
            return (1 - self.a) * x + self.a * x_next

    def step(self, v: np.ndarray | None = None):
        self.x = self(self.x, v)


def solution(dim, sr, seed, xmat, vmat):
    # DO NOT CHANGE HERE.
    net = ESN(dim, sr=sr, f=np.tanh, seed=seed)
    return net(xmat, v=vmat)


def dataset():
    random.seed(508712934712)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dim = random.randint(20, 50)
        sr = random.uniform(0, 2)
        ndim = random.randint(0, 2)
        seed = random.randint(0, 10000)
        shape = [random.randint(1, 3) for _ in range(ndim)]
        xmat = rnd.uniform(-1, 1, size=(*shape, dim))
        vmat = rnd.uniform(-1, 1, size=(*shape, dim)[random.randint(0, xmat.ndim) :])
        yield to_args(dim, sr, seed, xmat, vmat)
