from typing import Tuple

from solvers.solver import Solver
from utils.equations import Equation
from utils.math import d2f as _d2f
from utils.math import keeps_sign


class NewtonSolver(Solver):
    def check_convergence(self, equation: Equation):
        df, l, r = equation.df, equation.interval_l, equation.interval_r
        d2f = lambda x: _d2f(df, x)

        if not keeps_sign(df, l, r) or not keeps_sign(d2f, l, r):
            return False

        # f' = 0
        if df(l) == 0 or df(r) == 0:
            return False

        return True

    def get_starting_point(self, f, l, r):
        return l

    def solve(self, equation: Equation, precision: float) -> Tuple[float, int]:
        interval_l, interval_r, f, df = (
            equation.interval_l,
            equation.interval_r,
            equation.f,
            equation.df,
        )
        x = self.get_starting_point(f, interval_l, interval_r)
        prev_x = x - 10 * precision
        iterations = 0
        while True:
            iterations += 1
            x = x - f(x) / df(x)
            if (
                x - prev_x <= precision
                or abs(f(x) / df(x)) <= precision
                or abs(f(x)) <= precision
            ):
                break
            prev_x = x
        return x, iterations
