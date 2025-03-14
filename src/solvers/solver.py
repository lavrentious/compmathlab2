from typing import Callable, Tuple

from utils import df as _df


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

    def keeps_sign(self, f: Callable[[float], float], l: float, r: float):
        d = (r - l) / self.SAMPLES_COUNT
        x = l
        while x <= r:
            if not self.signs_equal(f(x), f(x + d)):
                return False
            x += d
        return True

    def signs_equal(self, a, b):
        return (a > 0 and b > 0) or (a < 0 and b < 0)

    def check_single_root(self, f: Callable[[float], float], l: float, r: float):
        df = lambda x: _df(f, x)

        if self.signs_equal(f(l), f(r)):
            return False  # 0 or even roots

        if self.keeps_sign(df, l, r):
            return True

        # manual check
        root_count = 0
        x = l
        d = (r - l) / self.SAMPLES_COUNT
        while x <= r:
            if not self.signs_equal(f(x), f(x + d)):
                root_count += 1
            if root_count > 1:
                return False
            x += d
        return True

    def check_convergence(
        self, f: Callable[[float], float], l: float, r: float
    ) -> bool:
        return True
