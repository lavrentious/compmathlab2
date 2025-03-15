from typing import Callable, List, Tuple


class SystemSolver:
    SAMPLES_COUNT = 1000

    def __init__(self):
        pass

    def solve(
        self,
        fs: List[Callable[[float], float]],
        precision: float,
    ) -> Tuple[float, int]:
        """
        @returns (x, iterations)
        """
        return 0, 0

    def check_convergence(self, fs: List[Callable[[float], float]]):
        pass
