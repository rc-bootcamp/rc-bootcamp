import random
import string

from utils.tester import to_args


def solution(s):
    return s.upper() == s[::-1].upper()


def dataset():
    yield to_args("1VCV1")
    yield to_args("abc")
    yield to_args("a121A")
    random.seed(3247832332)
    for _idx in range(97):
        length = random.randint(1, 100)
        s = "".join(random.choices(string.ascii_letters, k=length))
        if length > 1 and random.random() < 0.5:
            half = length // 2
            t = s[half::-1] if length % 2 == 0 else s[half + 1 :: -1]
            if random.random() < 0.5:
                s = s[:half] + t.swapcase()
        yield to_args(s)
