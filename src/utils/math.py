from typing import Callable, Tuple

import sympy as sp  # type: ignore

from config import PRECISION
from logger import GlobalLogger

SAMPLES_COUNT = 1000

type Number = int | float | sp.Float


logger = GlobalLogger()


def df(f: Callable[[Number], Number], x: Number) -> sp.Float:
    # return derivative(f, x)["df"]
    H = sp.Float("0.0001")
    return (f(x + H) - f(x - H)) / (2 * H)


def d2f(f: Callable[[Number], Number], x: Number) -> sp.Float:
    H = sp.Float("0.0001")
    return (f(x + H) - 2 * f(x) + f(x - H)) / H**2


def keeps_sign(f: Callable[[Number], Number], l: Number, r: Number) -> bool:
    d = (r - l) / SAMPLES_COUNT
    x = l
    while x <= r:
        if not signs_equal(f(x), f(x + d)):
            return False
        x += d
    return True


def signs_equal(a: Number, b: Number) -> bool:
    return (a > 0 and b > 0) or (a < 0 and b < 0)


def max_in_interval(f: Callable[[Number], Number], l: Number, r: Number) -> sp.Float:
    d = (r - l) / SAMPLES_COUNT
    x = l
    max_val = f(l)
    while x <= r:
        if f(x) > max_val:
            max_val = f(x)
        x += d
    return max_val


def min_in_interval(f: Callable[[Number], Number], l: Number, r: Number) -> sp.Float:
    d = (r - l) / SAMPLES_COUNT
    x = l
    min_val = f(l)
    while x <= r:
        if f(x) < min_val:
            min_val = f(x)
        x += d
    return min_val


def check_single_root(f: Callable[[Number], Number], l: Number, r: Number) -> bool:
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
    f: sp.Lambda, l: Number, r: Number
) -> Tuple[sp.Lambda, sp.Lambda]:
    """
    returns phi and phi' for a single variable function with lambda method
    """
    x = sp.symbols("x")
    f_expr = f(x)

    _df = sp.diff(f_expr, x)
    m = 1 / max_in_interval(lambda val: abs(_df.evalf(PRECISION).subs(x, val)), l, r)
    logger.debug("m", m)

    if _df.subs(x, (l + r) / 2) > 0:
        m *= -1

    phi = sp.Lambda(x, x + m * f_expr)
    dphi = sp.Lambda(x, 1 + m * _df)

    return phi, dphi
