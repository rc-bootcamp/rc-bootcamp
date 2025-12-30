import random
import string

from utils.tester import to_args


def solution(s):
    s0, s1 = s[0::2], s[1::2]
    if len(s0) == 0 or len(s1) == 0:
        return True
    if s0.isupper():
        return s1.islower()
    if s0.islower():
        return s1.isupper()
    return False


def dataset():
    yield to_args("AdB")
    yield to_args("ZLxs")
    yield to_args("a")
    yield to_args("D")
    random.seed(1928374122)
    for _idx in range(96):
        max_length = 100
        su = "".join(random.choices(string.ascii_uppercase, k=max_length))
        sl = "".join(random.choices(string.ascii_lowercase, k=max_length))
        s = "".join(sum(zip(su, sl, strict=False), ()))
        if random.random() < 0.5:
            lb = random.randint(0, len(s) - 2)
            le = random.randint(lb, lb + max_length)
            s = s[lb:le]
        else:
            s = "".join(random.choices(s, k=random.randint(0, max_length)))
        yield to_args(s)
