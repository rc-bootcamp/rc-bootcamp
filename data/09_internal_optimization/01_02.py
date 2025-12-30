import random

import numpy as np

from utils.reservoir import ESN, rls_update
from utils.tester import to_args
from utils.tqdm import tqdm


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
            self.P[post] = np.eye(len(self.w_pre[post])) / lmbd  # initialize P

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
                x = xn[self.w_pre[node_id]]  # use self.w_pre. (big hint: x = xn[...])
                P = self.P[node_id]  # self.P
                g, k, P_new = rls_update(P, x)  # use rls_update
                dw = g * np.outer(e, k)
                self.P[node_id] = P_new
                self.weight[node_id, self.w_pre[node_id]] += dw[0]
        return self.weight


def emulate_innate(
    ts,
    net,
    f_in=None,
    innate_range=None,
    innate_func=None,
    innate_node=None,
    innate_every=2,
    prefix="",
    leave=True,
    display=True,
):
    record = {}
    record["t"] = np.zeros(len(ts), dtype=int)
    record["x"] = np.zeros((len(ts), *net.x.shape))
    pbar = tqdm(ts, leave=leave, display=display)
    for cnt, t in enumerate(pbar):
        pbar.set_description("{}t={:.0f}".format(prefix, t))
        u_in = np.zeros_like(net.x)
        if f_in is not None:
            u_in += f_in(t)
        net.step(u_in)
        record["t"][cnt] = t
        record["x"][cnt] = net.x
        if (innate_range is not None) and (innate_range[0] <= t < innate_range[1]):
            if cnt % innate_every == 0:
                x_target = innate_func(t)
                net.train(x_target, node_list=innate_node)
    return record


def solution(ts, dim, seed, **kwargs):
    # DO NOT CHANGE HERE.
    net = InnateESN(dim, seed=seed)
    record = emulate_innate(ts, net, **kwargs)
    return record["x"]


def dataset():
    random.seed(398247932847879)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(20):
        dim = random.randint(50, 100)
        seed = random.randint(1, 10000000)
        ts = range(0, 10)
        innate_range = (5, 10)
        innate_node = range(0, random.randint(1, dim) - 1)
        innate_every = 1
        x_in = rnd.uniform(-1, 1, (len(ts), dim))
        x_target = rnd.uniform(-1, 1, (len(ts), dim))

        def f_in(t):
            return x_in[t]  # noqa: B023

        def innate_func(t):
            return x_target[t]  # noqa: B023

        yield to_args(
            ts,
            dim,
            seed,
            f_in=f_in,
            innate_range=innate_range,
            innate_func=innate_func,
            innate_node=innate_node,
            innate_every=innate_every,
            display=False,
        )
