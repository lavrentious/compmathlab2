import sys
import math
import re
from io import TextIOWrapper
from typing import Any, Callable

# sympy has no types :(
import sympy as sp  # type: ignore

from logger import GlobalLogger

logger = GlobalLogger()


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


class ResWriter:
    out_stream: TextIOWrapper | Any

    def __init__(self, out_stream: TextIOWrapper | Any = sys.stdout):
        self.out_stream = out_stream

    def write(self, equation_str: str, x: float, y: float, iterations: int):
        self.out_stream.write(f"{equation_str=}\n{x=}\nf(x)={y}\n{iterations=}")
        self.out_stream.flush()

    def destroy(self):
        self.out_stream.close()
