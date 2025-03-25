from typing import Dict, Tuple

import sympy as sp  # type: ignore

from logger import GlobalLogger
from solvers.system_solver import SystemSolver
from utils.equations import EquationSystem, EquationSystemSolution

logger = GlobalLogger()


class FixedPointIterationSystemSolver(SystemSolver):
    MAX_ITERATIONS = 100

    def __init__(self) -> None:
        pass

    def _starting_points_to_symbols(
        self, system: EquationSystem, starting_points: Dict[str, float]
    ) -> Dict[sp.Symbol, float]:
        system_symbols_strs = [s.name for s in system.symbols]
        if set(starting_points.keys()) != set(system_symbols_strs):
            raise ValueError("starting points do not match equation system symbols")
        return {sp.Symbol(k): v for k, v in starting_points.items()}

    def solve(
        self,
        system: EquationSystem,
        starting_points: Dict[str, float],
        precision: float,
    ) -> Tuple[EquationSystemSolution, int]:
        logger.debug(
            f"fixed point iteration: {system=} ; {precision=} ; {starting_points=}"
        )
        xs = self._starting_points_to_symbols(system, starting_points)
        prev_xs = {k: v - 10 * precision for k, v in xs.items()}
        iterations = 0
        for _ in range(self.MAX_ITERATIONS):
            iterations += 1
            xs = system.apply_phi(xs)
            if max(abs(xs[sym] - prev_xs[sym]) for sym in xs.keys()) <= precision:
                return xs, iterations
            prev_xs = xs.copy()
        raise ValueError("no convergence")

    def check_convergence(
        self, system: EquationSystem, starting_points: Dict[str, float]
    ) -> bool:
        # TODO
        return True
