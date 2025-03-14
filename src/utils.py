import re
from typing import Any, Callable

import sympy as sp
from scipy.differentiate import derivative


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
    allowed_pattern = r"^[x\d\s\+\-\*/\^(),\.]*$"
    if not re.match(allowed_pattern, equation_str):
        raise ValueError("Invalid characters in the equation")
    equation_str = equation_str.replace("^", "**")
    x = sp.symbols("x")
    try:
        expr = sp.sympify(equation_str.replace("^", "**"))
    except sp.SympifyError:
        raise ValueError("Invalid equation format")
    used_symbols = expr.free_symbols
    if len(used_symbols) != 1 or x not in used_symbols:
        raise ValueError(
            f"Invalid variable(s) {used_symbols - {x}} in the equation. Only 'x' is allowed."
        )
    func = sp.lambdify(x, expr, "math")
    return func


def df(f: Callable[[float], float], x: float) -> float:
    return derivative(f, x)["df"]


def d2f(f: Callable[[float], float], x: float) -> float:
    H = 0.0001
    return (f(x + H) - 2 * f(x) + f(x - H)) / H**2
