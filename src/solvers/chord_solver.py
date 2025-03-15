from typing import Tuple

from solvers.solver import Solver
from utils.equations import Equation
from utils.math import signs_equal


class ChordSolver(Solver):
    def solve(self, equation: Equation, precision: float) -> Tuple[float, int]:
        a, b = equation.interval_l, equation.interval_r
        f = equation.f
        prev_x = a - 10 * precision
        iterations = 0
        while True:
            x = a - (b - a) / (f(b) - f(a)) * f(a)
            if signs_equal(f(x), f(a)):
                a = x
            else:
                b = x
            iterations += 1
            if (
                x - prev_x <= precision
                or abs(a - b) <= precision
                or abs(f(x)) <= precision
            ):
                break
            prev_x = x
        return x, iterations
