import random

import numpy as np
import scipy as sp

from utils.tester import to_args


def get_maxima_and_minima(xs, **kwargs):
    id_maxima = sp.signal.find_peaks(xs, **kwargs)[0]
    id_minima = sp.signal.find_peaks(-xs, **kwargs)[0]
    return id_maxima, id_minima


def solution(*args, **kwargs):
    id_maxima, id_minima = get_maxima_and_minima(*args, **kwargs)
    sum = np.sum(id_maxima) + np.sum(id_minima)
    return sum


def dataset():
    random.seed(1238201)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(100, 1000)
        xs = rnd.uniform(0, 1, t)
        yield to_args(xs)
