#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import numpy as np


def narma_func(us, y_init, alpha=0.3, beta=0.05, gamma=1.5, delta=0.1, mu=0.25, kappa=0.25):
    assert us.shape[0] > 10
    assert y_init.shape[0] == 10
    assert y_init.shape[1:] == us.shape[1:]
    vs = mu * us + kappa
    ys = np.zeros_like(vs)
    ys[:10] = y_init
    for idx in range(10, ys.shape[0]):
        ys[idx] += alpha * ys[idx - 1]
        ys[idx] += beta * ys[idx - 1] * np.sum(ys[idx - 10 : idx], axis=0)
        ys[idx] += gamma * vs[idx - 10] * vs[idx - 1]
        ys[idx] += delta
    return ys
