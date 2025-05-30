from typing import Callable, Dict, Tuple

import sympy as sp  # type: ignore

from utils.equations import EquationSystem, EquationSystemSolution


class SystemSolver:
    SAMPLES_COUNT = 1000

    def __init__(self) -> None:
        pass

    def solve(
        self,
        system: EquationSystem,
        starting_xs: Dict[str, sp.Float],
        precision: sp.Float,
        on_iteration: Callable[[EquationSystemSolution, int], None] | None = None,
    ) -> Tuple[EquationSystemSolution, int] | None:
        """
        @returns (x, iterations)
        """
        return None

    def check_convergence(
        self, system: EquationSystem, starting_xs: Dict[str, sp.Float]
    ) -> bool:
        return True
