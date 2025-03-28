from typing import Tuple

import sympy as sp  # type: ignore

from utils.equations import Equation


class Solver:
    SAMPLES_COUNT = 1000

    def __init__(self) -> None:
        pass

    def solve(
        self,
        equation: Equation,
        precision: sp.Float,
    ) -> Tuple[sp.Float, int]:
        """
        @returns (x, iterations)
        """
        return 0, 0

    def check_convergence(self, equation: Equation) -> bool:
        return True
