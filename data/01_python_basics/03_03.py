import random
import string

from utils.tester import to_args


def solution(s):
    return s.replace("two", "2")


def dataset():
    yield to_args("network")
    yield to_args("town")
    random.seed(58793874294)
    for _idx in range(98):
        length = random.randint(1, 100)
        s = "".join(random.choices(string.ascii_letters + string.digits, k=length))
        if random.random() < 0.8:
            s = s.replace("2", "two")
        yield to_args(s)
