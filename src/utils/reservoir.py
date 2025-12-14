#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import math

import numpy as np
from scipy.sparse.linalg import ArpackNoConvergence, eigs


class Module(object):
    def __init__(self, *_args, seed=None, rnd=None, dtype=np.float64, **_kwargs):
        if rnd is None:
            self.rnd = np.random.default_rng(seed)
        else:
            self.rnd = rnd
        self.dtype = dtype


class Linear(Module):
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        bound: float | None = None,
        weight: np.ndarray | None = None,
        bias: float = 0.0,
        **kwargs,
    ):
        """
        Linear model

        Args:
            input_dim (int): input dimension
            output_dim (int): output dimension
            bound (float, optional): sampling scale for weight. Defaults to None.
            bias (float, optional): sampling scale for bias. Defaults to 0.0.
            weight (np.ndarray | None, optional): weight matrix. Defaults to None.
        """
        super(Linear, self).__init__(**kwargs)
        self.input_dim = input_dim
        self.output_dim = output_dim
        if bound is None:
            bound = math.sqrt(1 / input_dim)
        if weight is None:
            self.weight = self.rnd.uniform(-bound, bound, (output_dim, input_dim)).astype(self.dtype)
        else:
            self.weight = np.asarray(weight, dtype=self.dtype)
            assert self.weight.shape[-2:] == (output_dim, input_dim)
        self.bias = self.rnd.uniform(-bias, bias, (output_dim,)).astype(self.dtype)

    def __call__(self, x: np.ndarray):
        x = np.asarray(x)
        out = np.matmul(x, self.weight.swapaxes(-1, -2)) + self.bias
        return out


class RidgeReadout(Linear):
    def __init__(self, *args, lmbd: float | None = None, **kwargs):
        """
        Linear model supporting Ridge regression

        Args:
            lmbd (float): regularization term. Defaults to None.
        """
        super(RidgeReadout, self).__init__(*args, **kwargs)
        self.lmbd = lmbd

    def train(self, x: np.ndarray, y: np.ndarray):
        """
        Run Ridge regression and update the weight and bias.
        Supporting batch update.

        Args:
            x (np.ndarray): inputs, shape (..., size, input_dim)
            y (np.ndarray): targets, shape (..., size, output_dim)
        Returns:
            self.weight (np.ndarray):
            self.bias (np.ndarray):
        """
        assert (x.ndim > 1) and (x.shape[-1] == self.input_dim)
        assert (y.ndim > 1) and (y.shape[-1] == self.output_dim)
        *batch_size, _data_size, _input_dim = x.shape
        x_biased = np.ones((*x.shape[:-1], self.input_dim + 1), dtype=self.dtype)
        x_biased[..., 1:] = x
        xtx = x_biased.swapaxes(-2, -1) @ x_biased
        xty = x_biased.swapaxes(-2, -1) @ y
        if self.lmbd is not None:
            xtx += self.lmbd * np.eye(self.input_dim + 1)
        sol = np.matmul(np.linalg.pinv(xtx), xty)
        self.weight = sol[..., 1:, :].swapaxes(-2, -1)
        self.bias = sol[..., :1, :] if len(batch_size) > 0 else sol[..., 0, :]
        return self.weight, self.bias


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
        weight: np.ndarray | None = None,
        **kwargs,
    ):
        """
        Echo state network [Jaeger, H. (2001). Bonn, Germany:
        German National Research Center for Information Technology GMD Technical Report, 148(34), 13.]

        Args:
            dim (int): number of the ESN nodes
            sr (float, optional): spectral radius. Defaults to 1.0.
            f (callable | None, optional): activation function. None means no activation. Defaults to np.tanh.
            a (float | None, optional): leaky rate. Defaults to None.
            p (float, optional): density of connection matrix. Defaults to 1.0.
            init_state (np.ndarray | None, optional): initial states. Defaults to None.
            normalize (bool, optional): decide if normalizing connection matrix. Defaults to True.
            weight (np.ndarray | None, optional): connection matrix. Defaults to None.
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
                if weight is not None:
                    self.weight = np.array(weight, dtype=self.dtype)
                    assert self.weight.shape == (dim, dim)
                    break
                self.weight = self.rnd.normal(size=(self.dim, self.dim)).astype(self.dtype)
                if self.p < 1.0:
                    w_con = np.full((dim * dim,), False)
                    w_con[: int(dim * dim * self.p)] = True
                    self.rnd.shuffle(w_con)
                    w_con = w_con.reshape((dim, dim))
                    self.weight = self.weight * w_con
                if not normalize:
                    break
                eigen_values = eigs(self.weight, return_eigenvectors=False, k=1, which="LM", v0=np.ones(self.dim))
                spectral_radius = max(abs(eigen_values))
                self.weight = self.weight / spectral_radius
                break
            except ArpackNoConvergence:
                continue

    def __call__(self, x: np.ndarray, v=None):
        x_next = self.sr * np.matmul(x, self.weight.swapaxes(-1, -2))
        if v is not None:
            x_next += v
        if self.f is not None:
            x_next = self.f(x_next)
        if self.a is None:
            return x_next
        else:
            return (1 - self.a) * x + self.a * x_next

    def step(self, v=None):
        self.x = self(self.x, v)


def rls_update(P, x):
    k = np.dot(P, x)
    g = 1 / (1 + x.dot(k))
    dP = g * np.outer(k, k)
    P_new = P - dP
    return g, k, P_new
