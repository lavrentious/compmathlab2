from typing import Dict, Tuple

import sympy as sp  # type: ignore

from utils.equations import EquationSystem, EquationSystemSolution


class SystemSolver:
    SAMPLES_COUNT = 1000

    def __init__(self) -> None:
        pass

    def solve(
        self,
        system: EquationSystem,
        starting_points: Dict[str, float],
        precision: float,
    ) -> Tuple[EquationSystemSolution, int]:
        """
        @returns (x, iterations)
        """
        return {}, 0

    def check_convergence(
        self, system: EquationSystem, starting_points: Dict[str, float]
    ) -> bool:
        return True
