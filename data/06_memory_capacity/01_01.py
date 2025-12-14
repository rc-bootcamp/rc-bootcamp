import random

import numpy as np

from utils.tester import to_args


def calc_regression_and_rank(X):
    T, N = X.shape[-2:]
    X = X - X.mean(axis=-2, keepdims=True)  # mean centering
    U, sigma, V = np.linalg.svd(X, full_matrices=False)  # calculate SVD
    eps = np.finfo(X.dtype).eps
    sigma_sq_max = np.max(sigma * sigma, axis=-1, keepdims=True)
    eps = sigma_sq_max * (eps * max(T, N))
    mask = sigma > eps
    rank = mask.sum(axis=-1)  # calculate rank
    return U, mask, rank


solution = calc_regression_and_rank


def dataset():
    random.seed(45375943543)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        T = random.randint(10, 1000)
        N = random.randint(1, 100)
        M = random.randint(0, N // 10)
        arr = rnd.uniform(-100, 100, size=(T, N))
        if M > 0:
            arr[..., :M] = arr[..., -M:]
        yield to_args(arr)
