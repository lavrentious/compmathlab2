from typing import Tuple

from solvers.solver import Solver
from utils import d2f as _d2f
from utils import df as _df


class NewtonSolver(Solver):
    def check_convergence(self, f, l, r):
        df = lambda x: _df(f, x)
        d2f = lambda x: _d2f(f, x)

        if not self.keeps_sign(df, l, r) or not self.keeps_sign(d2f, l, r):
            return False

        # f' = 0
        if df(l) == 0 or df(r) == 0:
            return False

        return True

    def get_starting_point(self, f, l, r):
        return l

    def solve(self, f, interval_l, interval_r, precision) -> Tuple[float, int]:
        df = lambda x: _df(f, x)

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
