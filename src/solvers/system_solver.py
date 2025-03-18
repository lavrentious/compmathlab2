from typing import List, Tuple

from utils.equations import EquationSystem, MultivariableEquation


class SystemSolver:
    SAMPLES_COUNT = 1000

    def __init__(self):
        pass

    def solve(
        self,
        system: EquationSystem,
        precision: float,
    ) -> Tuple[List[float], int]:
        """
        @returns (x, iterations)
        """
        return [], 0

    def check_convergence(self, system: EquationSystem):
        pass
