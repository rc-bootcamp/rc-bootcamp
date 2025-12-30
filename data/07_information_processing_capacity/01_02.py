import random

import numpy as np

from utils.tester import to_args


def calc_inner_product(a, b):
    return a.dot(b) / np.linalg.norm(a) / np.linalg.norm(b)


solution = calc_inner_product


def dataset():
    random.seed(8901672597439)
    rnd = np.random.default_rng(random.randint(0, (2 << 63) - 1))
    for _idx in range(100):
        t = random.randint(10, 1000)
        arr_a = rnd.uniform(-1, 1, size=(t,))
        arr_b = rnd.uniform(-1, 1, size=(t,))
        yield to_args(arr_a, arr_b)
