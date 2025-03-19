from typing import Tuple

from logger import GlobalLogger
from solvers.system_solver import SystemSolver
from utils.equations import EquationSystem, EquationSystemSolution

logger = GlobalLogger()


class FixedPointIterationSystemSolver(SystemSolver):
    MAX_ITERATIONS = 100

    def __init__(self) -> None:
        pass

    def get_starting_points(self, system: EquationSystem) -> EquationSystemSolution:
        return {k: 1 for k in system.symbols}

    def solve(
        self,
        system: EquationSystem,
        precision: float,
    ) -> Tuple[EquationSystemSolution, int]:
        xs = self.get_starting_points(system)
        prev_xs = {k: v - 10 * precision for k, v in xs.items()}
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            xs = system.apply_phi(xs)
            if max(abs(xs[sym] - prev_xs[sym]) for sym in xs.keys()) <= precision:
                return xs, iterations
            prev_xs = xs.copy()
        raise ValueError("no convergence")

    def check_convergence(self, system: EquationSystem) -> bool:
        # TODO
        return True
