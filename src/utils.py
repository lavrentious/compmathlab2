import math
import re
from typing import Any, Callable

import sympy as sp
from scipy.differentiate import derivative

from logger import GlobalLogger

logger = GlobalLogger()


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


def validate_and_parse_equation(equation_str: str) -> Callable[[float], float]:
    equation_str = equation_str.replace(",", ".").replace("^", "**")
    allowed_functions = (
        "("
        + "|".join(
            filter(
                lambda s: not s.startswith("_")
                and not s.endswith("_")
                and s not in {"inf", "nan"},
                math.__dict__.keys(),
            )
        )
        + ")"
    )
    allowed_pattern = r"^[0-9+\-*/().^ \s" + allowed_functions + "]+$"
    if not re.match(allowed_pattern, equation_str):
        raise ValueError("Invalid characters in the equation")
    x = sp.symbols("x")
    try:
        expr = sp.sympify(equation_str)
    except sp.SympifyError:
        raise ValueError("Invalid equation format")
    used_symbols = expr.free_symbols
    if len(used_symbols) > 1:
        raise ValueError(
            f"Invalid variable(s) {used_symbols - {x}} in the equation. Only 'x' is allowed."
        )
    logger.debug("parsed expression", expr)
    func = sp.lambdify(x, expr, "math")
    return func


def df(f: Callable[[float], float], x: float) -> float:
    # return derivative(f, x)["df"]
    H = 0.0001
    return (f(x + H) - f(x - H)) / (2 * H)


def d2f(f: Callable[[float], float], x: float) -> float:
    H = 0.0001
    return (f(x + H) - 2 * f(x) + f(x - H)) / H**2
