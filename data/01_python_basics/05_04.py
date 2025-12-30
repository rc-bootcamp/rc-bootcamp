import random

from utils.tester import to_args


def solution(n, m):
    is_prime = [True] * (m + 1)
    is_prime[0] = False
    is_prime[1] = False
    for p in range(2, m + 1):
        if p * p > m:
            break
        if not (is_prime[p]):
            continue
        for k in range(2 * p, m + 1, p):
            is_prime[k] = False
    summation = 0
    for p in range(n, m + 1):
        if is_prime[p]:
            summation += p
    return summation

    # Alternative solution.
    # return sum(filter(range(n, m + 1), lambda pos: is_prime[pos]))


def dataset():
    yield to_args(1, 11)
    yield to_args(2, 2)
    yield to_args(4, 4)
    yield to_args(100, 1000)
    random.seed(93827041098)
    for _idx in range(96):
        n = random.randint(1, 10000)
        m = random.randint(n, 10000)
        yield to_args(n, m)
