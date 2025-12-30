#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

__all__ = ["BatchRegressor"]

import functools
import math
import operator

from .helper import backend_max, backend_std, import_backend
from .polynomial import BasePolynomial


class BatchRegressor(object):
    """
    BatchRegressor performs singular value decomposition (SVD) on the provided time series data `xs`
    and uses the resulting left singular vectors to compute the regression of polynomial features.
    """

    def __init__(self, xs, offset=1000, debias=True, normalize=False, threshold_mode="linear"):
        """
        Parameters:
            xs (ndarray): Time series data with shape [*batch_shape, T, D].
            offset (int, optional): Offset applied to the time series data.
            debias (bool, optional): Removes the mean from the data if set to True.
            normalize (bool, optional): Scales the data to unit variance if set to True.
            threshold_mode (str, optional): Determines the singular value thresholding mode, either 'linear' or 'sqrt'.

        Notes:
            `BatchRegressor` is used inside `UnivariateProfiler` and is not intended to be used directly by users.
            The behavior of the regressor can be specified when you create an instance of `UnivariateProfiler`.

        """
        self.backend = import_backend(xs)
        self.offset, self.length = offset, xs.shape[-2]
        if debias:
            xs = xs - xs[..., self.offset :, :].mean(axis=-2, keepdims=True)
        if normalize:
            std = backend_std(xs[..., self.offset :, :], axis=-2, keepdims=True)
            std[std < self.backend.finfo(std.dtype).eps] = 1.0
            xs = xs / std
        self.left, self.sigma, _right = self.backend.linalg.svd(
            xs[..., self.offset :, :], full_matrices=False
        )
        # -> [*bs, T, D], [*bs, D], [*bs, D, D]
        # See https://numpy.org/devdocs/reference/generated/numpy.linalg.matrix_rank.html
        self.eps = self.backend.finfo(self.sigma.dtype).eps
        m, n = xs.shape[-2:]
        sigma_sq_max = backend_max(self.sigma * self.sigma, axis=-1, keepdims=True)  # [*bs, D]
        if threshold_mode == "linear":
            self.eps = sigma_sq_max * (self.eps * max(m, n))
        elif threshold_mode == "sqrt":
            self.eps = sigma_sq_max * (self.eps * 0.5 * math.sqrt(m + n + 1))
        self.mask = (self.sigma > self.eps)[..., None]  # [*bs, D, 1]

    @property
    def rank(self):
        return self.mask.sum(axis=(-2, -1))

    def calc(self, y):
        dot = self.backend.matmul(
            self.left.swapaxes(-2, -1), y
        )  # [*bs, T, D], [*bs, T, Y] -> [*bs, D, Y]
        dot = ((dot * dot) * self.mask).sum(axis=-2)  # [*bs, D, Y], [*bs, D, 1] -> [*bs, Y]
        var = (y * y).sum(axis=-2)  # [*bs, T, Y] -> [*bs, Y]
        return dot / var

    def __call__(self, poly: BasePolynomial, degrees: tuple[int], delays: tuple[int], formatter=()):
        target = functools.reduce(
            operator.mul,
            [
                poly[(deg, *formatter)][..., self.offset - gap : self.length - gap, :]
                for deg, gap in zip(degrees, delays, strict=False)
            ],
            1,
        )
        return self.calc(target)
