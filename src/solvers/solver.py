from typing import Tuple

from utils.equations import Equation


class Solver:
    SAMPLES_COUNT = 1000

    def __init__(self) -> None:
        pass

    def solve(
        self,
        equation: Equation,
        precision: float,
    ) -> Tuple[float, int]:
        """
        @returns (x, iterations)
        """
        return 0, 0

    def check_convergence(self, equation: Equation) -> bool:
        return True
