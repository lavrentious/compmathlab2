from typing import Tuple

import sympy as sp  # type: ignore

from logger import GlobalLogger
from solvers.solver import Solver
from utils.equations import Equation


logger = GlobalLogger()


class FixedPointIterationSolver(Solver):
    MAX_ITERATIONS = 100000
    Q = 1  # 0 <= q < 1

    def __init__(self) -> None:
        super().__init__()

    def get_starting_point(
        self, equation: Equation, l: sp.Float, r: sp.Float
    ) -> sp.Float:
        return (l + r) / 2

    def solve(
        self, equation: Equation, precision: sp.Float
    ) -> Tuple[sp.Float, int] | None:
        logger.debug("solving fixed point iteration")
        logger.debug(f"precision: {type(precision)} {precision}")
        logger.debug(f"interval_l: {type(equation.interval_l)} {equation.interval_l}")
        logger.debug(f"interval_r: {type(equation.interval_r)} {equation.interval_r}")

        interval_l, interval_r, fn, phi = (
            equation.interval_l,
            equation.interval_r,
            equation.f,
            equation.phi,
        )
        x = self.get_starting_point(fn, interval_l, interval_r)
        prev_x = x - 10 * precision
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            x = phi(x)
            if abs(x - prev_x) <= precision:
                return x, iterations
            prev_x = x
        return None

    def check_convergence(self, equation: Equation) -> bool:
        l, r, dphi = (
            equation.interval_l,
            equation.interval_r,
            equation.dphi,
        )
        d = (r - l) / self.SAMPLES_COUNT
        x = l
        while x <= r:
            if abs(dphi(x)) > self.Q:
                return False
            x += d
        return True
