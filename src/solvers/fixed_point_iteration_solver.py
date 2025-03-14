import matplotlib.pyplot as plt
import numpy as np
from typing import Callable, Tuple
from solvers.solver import Solver
from utils import df as _df


class FixedPointIterationSolver(Solver):
    MAX_ITERATIONS = 100000
    Q = 1  # 0 <= q < 1

    def __init__(self):
        super().__init__()

    def get_phi(
        self, f: Callable[[float], float], l: float, r: float
    ) -> Tuple[Callable[[float], float], Callable[[float], float]]:
        """
        returns phi and phi'
        """
        df = lambda x: _df(f, x)

        m = 1 / self.max_in_interval(lambda x: abs(df(x)), l, r)
        if df((l + r) / 2) > 0:
            m *= -1
        print(f"{m=}")
        phi = lambda x: x + m * f(x)
        dphi = lambda x: 1 + m * df(x)
        return phi, dphi

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
        _, dphi = self.get_phi(f, l, r)

        d = (r - l) / self.SAMPLES_COUNT
        x = l
        while x <= r:
            if abs(dphi(x)) > self.Q:
                return False
            x += d
        return True
