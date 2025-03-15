from typing import Callable, Tuple


class Solver:
    SAMPLES_COUNT = 1000

    def __init__(self):
        pass

    def solve(
        self,
        fn: Callable[[float], float],
        interval_l: float,
        interval_r: float,
        precision: float,
    ) -> Tuple[float, int]:
        """
        @returns (x, iterations)
        """
        return 0, 0

    def check_convergence(
        self, f: Callable[[float], float], l: float, r: float
    ) -> bool:
        return True
