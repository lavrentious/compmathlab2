from typing import Tuple

import sympy as sp  # type: ignore

from solvers.solver import Solver
from utils.equations import Equation
from utils.math import d2f as _d2f
from utils.math import keeps_sign


class NewtonSolver(Solver):
    MAX_ITERATIONS = 100

    def check_convergence(self, equation: Equation) -> bool:
        df, l, r = equation.df, equation.interval_l, equation.interval_r
        d2f = lambda x: _d2f(df, x)

        if not keeps_sign(df, l, r) or not keeps_sign(d2f, l, r):
            return False

        # f' = 0
        if df(l) == 0 or df(r) == 0:
            return False

        return True

    def get_starting_point(
        self, equation: Equation, l: sp.Float, r: sp.Float
    ) -> sp.Float:
        return l

    def solve(
        self, equation: Equation, precision: sp.Float
    ) -> Tuple[sp.Float, int] | None:
        interval_l, interval_r, f, df = (
            equation.interval_l,
            equation.interval_r,
            equation.f,
            equation.df,
        )
        x = self.get_starting_point(equation, interval_l, interval_r)
        prev_x = x - 10 * precision
        for i in range(self.MAX_ITERATIONS):
            x = x - f(x) / df(x)
            if (
                x - prev_x <= precision
                or abs(f(x) / df(x)) <= precision
                or abs(f(x)) <= precision
            ):
                return x, i
            prev_x = x
        return None
