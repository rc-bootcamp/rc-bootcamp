import random

import numpy as np

from utils.tester import to_args


def reshape_lr(lr):
    lr_new = lr[:, None]
    return lr_new


def solution(*args, **kwargs):
    return reshape_lr(*args, **kwargs)


def dataset():
    random.seed(493574987129342)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        dims = random.randint(1, 200)
        rhos = rnd.uniform(0.0, 1.0, size=(dims,))
        yield to_args(rhos)
