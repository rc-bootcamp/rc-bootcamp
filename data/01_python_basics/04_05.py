import random
import string

from utils.tester import to_args


def solution(n):
    s = str(n)[::-1]
    ans = []
    for pos in range(0, len(s), 4):
        ans.append(s[pos : pos + 4])
    return "_".join(ans)[::-1]

    # Alternative solution.
    # return '_'.join(s[idx:idx + 4:] for idx in range(0, len(s), 4))[::-1]


def dataset():
    yield to_args(123456)
    yield to_args(123456789)
    random.seed(4897192674)
    for _idx in range(98):
        length = random.randint(1, 20)
        n = "".join(random.choices(string.digits, k=length))
        n = str(n)
        yield to_args(n)
