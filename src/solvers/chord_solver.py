from typing import Tuple

import sympy as sp  # type: ignore

from solvers.solver import Solver
from utils.equations import Equation
from utils.math import signs_equal


MAX_ITERATIONS = 100


class ChordSolver(Solver):
    def solve(self, equation: Equation, precision: sp.Float) -> Tuple[sp.Float, int] | None:
        a, b = equation.interval_l, equation.interval_r
        f = equation.f
        prev_x = a - 10 * precision
        for i in range(MAX_ITERATIONS):
            x = a - (b - a) / (f(b) - f(a)) * f(a)
            if signs_equal(f(x), f(a)):
                a = x
            else:
                b = x
            if (
                x - prev_x <= precision
                or abs(a - b) <= precision
                or abs(f(x)) <= precision
            ):
                return x, i + 1
            prev_x = x
        return None
