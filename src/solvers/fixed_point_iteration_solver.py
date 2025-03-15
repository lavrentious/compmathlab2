from typing import Callable, Tuple

from solvers.solver import Solver
from utils.math import df as _df


class FixedPointIterationSolver(Solver):
    MAX_ITERATIONS = 100000
    Q = 1  # 0 <= q < 1

    def __init__(self):
        super().__init__()

    def get_starting_point(self, f, l, r):
        return (l + r) / 2

    def solve(self, fn, interval_l, interval_r, precision):
        phi, _ = self.get_phi(fn, interval_l, interval_r)
        x = self.get_starting_point(fn, interval_l, interval_r)
        prev_x = x - 10 * precision
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            x = phi(x)
            if abs(x - prev_x) <= precision:
                return x, iterations
            prev_x = x
        raise ValueError("no convergence")

    def check_convergence(self, f, l, r):
        _, dphi = get_phi(f, l, r)

        d = (r - l) / self.SAMPLES_COUNT
        x = l
        while x <= r:
            if abs(dphi(x)) > self.Q:
                return False
            x += d
        return True
