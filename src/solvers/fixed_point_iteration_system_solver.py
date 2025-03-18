from typing import List, Tuple

from solvers.system_solver import SystemSolver
from utils.equations import EquationSystem, MultivariableEquation


class FixedPointIterationSystemSolver(SystemSolver):
    MAX_ITERATIONS = 100

    def __init__(self):
        pass

    def get_starting_points(self, system: EquationSystem):
        return [1.0] * len(system.equations)

    def solve(
        self,
        system: EquationSystem,
        precision: float,
    ) -> Tuple[List[float], int]:
        xs = self.get_starting_points(system)
        prev_x = [x - 10 * precision for x in xs]
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            xs = [e.phi(*xs) for e in system.equations]
            if max(abs(x - prev_x) for x, prev_x in zip(xs, prev_x)) <= precision:
                return xs, iterations
            prev_x = xs.copy()
        raise ValueError("no convergence")

    def check_convergence(self, system: EquationSystem):
        # TODO
        return True
