import random

from utils.tester import to_args


def solution(n):
    if n % 1111 == 0:
        return -1
    cnt = 0
    while n != 6174:
        s = sorted("{:04d}".format(n))
        n = int("".join(s[::-1])) - int("".join(s))
        cnt += 1
    return cnt

    # Alternative solution.
    # if n % 1111 == 0:
    #     return -1
    # if n == 6174:
    #     return 0
    # s = sorted('{:04d}'.format(n))
    # diff = int(''.join(s[::-1])) - int(''.join(s))
    # return 1 + solution(diff)


def dataset():
    yield to_args(3524)
    yield to_args(6174)
    yield to_args(5555)
    random.seed(290812417)
    for _idx in range(97):
        n = random.randint(1000, 9999)
        yield to_args(n)
