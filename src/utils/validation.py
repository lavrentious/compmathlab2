from typing import Any


def is_float(s: Any):
    if type(s) == float:
        return True
    if type(s) == str:
        s = s.replace(",", ".")
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s: Any):
    try:
        int(s)
        return True
    except ValueError:
        return False


def to_float(s: Any):
    if type(s) == float:
        return s
    if type(s) == str:
        s = s.replace(",", ".")
    return float(s)
