import random

import numpy as np

from utils.reservoir import ESN, rls_update
from utils.tester import to_args


class InnateESN(ESN):
    def __init__(self, *args, lmbd=1.0, **kwargs):
        """
        Tunable ESN [Laje, R., & Buonomano, D. V. (2013). Nature neuroscience, 16(7), 925-933.]

        Args:
            alpha (float, optional): regularization parameter for RLS algorithm. Defaults to 1.0.
        """
        super(InnateESN, self).__init__(*args, **kwargs)
        self.w_pre = {}
        self.P = {}
        for post in range(self.dim):
            non_zeros = self.weight[post].nonzero()[0]
            self.w_pre[post] = non_zeros
            self.P[post] = np.eye(len(self.w_pre[post])) / lmbd

    def train(self, x_target, x_now=None, node_list=None):
        """
        Update the internal weight by RLS algorithm

        Args:
            x_target (np.ndarray): State(s) on an inante trajectory.
            x_now (np.ndarray, optional): Current state(s). Defaults to None (use self.x).
            node_list (list, slice, optional): Tuned nodes. Defaults to None (train all nodes).
        """
        if x_now is None:
            x_now = np.asarray(self.x)
        if node_list is None:
            node_list = range(self.dim)
        for xt, xn in zip(x_target.reshape(-1, self.dim), x_now.reshape(-1, self.dim), strict=False):
            es = xt[node_list] - xn[node_list]
            for node_id, e in zip(node_list, es, strict=False):
                x = xn[self.w_pre[node_id]]
                P = self.P[node_id]
                g, k, P_new = rls_update(P, x)
                dw = g * np.outer(e, k)
                self.P[node_id] = P_new
                self.weight[node_id, self.w_pre[node_id]] += dw[0]
        return self.weight


def solution(dim, seed, x_target, x_now, node_list):
    # DO NOT CHANGE HERE.
    net = InnateESN(dim, seed=seed, node_list=node_list)
    net.train(x_target=x_target, x_now=x_now, node_list=node_list)
    return net.weight


def dataset():
    random.seed(1239472189798372)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        dim = random.randint(50, 100)
        seed = random.randint(1, 10000000)
        node_list = range(0, random.randint(1, dim) - 1)
        x_target = rnd.uniform(-1, 1, (random.randint(1, 3), dim))
        x_now = rnd.uniform(-1, 1, x_target.shape)
        yield to_args(dim, seed, x_target, x_now, node_list)
