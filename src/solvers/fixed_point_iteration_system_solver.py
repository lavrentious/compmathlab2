from typing import Callable, List, Tuple

from solvers.system_solver import SystemSolver
from utils.equations import MultivariableEquation


class FixedPointIterationSystemSolver(SystemSolver):
    MAX_ITERATIONS = 100

    def __init__(self):
        pass

    def get_starting_points(self, equations: List[MultivariableEquation]):
        return [1.0] * len(equations)

    def solve(
        self,
        equations: List[MultivariableEquation],
        precision: float,
    ) -> Tuple[List[float], int]:
        assert len(equations) > 0
        n = len(equations[0].f.expr.free_symbols)
        assert all(len(e.f.expr.free_symbols) <= n for e in equations)

        xs = self.get_starting_points(equations)
        prev_x = [x - 10 * precision for x in xs]
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            xs = [e.phi(*xs) for e in equations]
            if max(abs(x - prev_x) for x, prev_x in zip(xs, prev_x)) <= precision:
                return xs, iterations
            prev_x = xs.copy()
        raise ValueError("no convergence")

    def check_convergence(self, fs: List[MultivariableEquation]):
        # TODO
        return True
