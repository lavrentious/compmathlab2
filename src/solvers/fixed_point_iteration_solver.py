from typing import Callable

from solvers.solver import Solver
from utils import df as _df


class FixedPointIterationSolver(Solver):
    MAX_ITERATIONS = 100000
    Q = 1  # 0 <= q < 1
    g: Callable[[float], float]

    def __init__(self):
        super().__init__()

    def set_g(self, g: Callable[[float], float]):
        self.g = g

    def get_starting_point(self, f, l, r):
        return (l + r) / 2

    def solve(self, fn, interval_l, interval_r, precision):
        x = self.get_starting_point(fn, interval_l, interval_r)
        prev_x = x - 10 * precision
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            x = self.g(x)
            if abs(x - prev_x) <= precision:
                return x, iterations
            prev_x = x
        raise ValueError("no convergence")

    def check_convergence(self, f, l, r):
        dg = lambda x: _df(self.g, x)

        d = (r - l) / self.SAMPLES_COUNT
        x = l
        while x <= r:
            if abs(dg(x)) > self.Q:
                return False
            x += d
        return True
