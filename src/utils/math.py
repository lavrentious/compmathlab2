from typing import Callable, Tuple

SAMPLES_COUNT = 1000


def df(f: Callable[[float], float], x: float) -> float:
    # return derivative(f, x)["df"]
    H = 0.0001
    return (f(x + H) - f(x - H)) / (2 * H)


def d2f(f: Callable[[float], float], x: float) -> float:
    H = 0.0001
    return (f(x + H) - 2 * f(x) + f(x - H)) / H**2


def keeps_sign(f: Callable[[float], float], l: float, r: float):
    d = (r - l) / SAMPLES_COUNT
    x = l
    while x <= r:
        if not signs_equal(f(x), f(x + d)):
            return False
        x += d
    return True


def signs_equal(a, b):
    return (a > 0 and b > 0) or (a < 0 and b < 0)


def max_in_interval(f: Callable[[float], float], l: float, r: float):
    d = (r - l) / SAMPLES_COUNT
    x = l
    max_val = f(l)
    while x <= r:
        if f(x) > max_val:
            max_val = f(x)
        x += d
    return max_val


def min_in_interval(f: Callable[[float], float], l: float, r: float):
    d = (r - l) / SAMPLES_COUNT
    x = l
    min_val = f(l)
    while x <= r:
        if f(x) < min_val:
            min_val = f(x)
        x += d
    return min_val


def check_single_root(f: Callable[[float], float], l: float, r: float):
    _df = lambda x: df(f, x)

    if signs_equal(f(l), f(r)):
        return False  # 0 or even roots

    if keeps_sign(_df, l, r):
        return True

    # manual check
    root_count = 0
    x = l
    d = (r - l) / SAMPLES_COUNT
    while x <= r:
        if not signs_equal(f(x), f(x + d)):
            root_count += 1
        if root_count > 1:
            return False
        x += d
    return True


def get_phi_with_lambda(
    f: Callable[[float], float], l: float, r: float
) -> Tuple[Callable[[float], float], Callable[[float], float]]:
    """
    returns phi and phi' for a single variable function with lambda method
    """
    _df = lambda x: df(f, x)

    m = 1 / max_in_interval(lambda x: abs(_df(x)), l, r)
    if _df((l + r) / 2) > 0:
        m *= -1
    print(f"{m=}")
    phi = lambda x: x + m * f(x)
    dphi = lambda x: 1 + m * _df(x)
    return phi, dphi
