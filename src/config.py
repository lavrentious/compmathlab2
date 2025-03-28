from mpmath import mp  # type: ignore

from utils.meta import singleton

EPS = 0.0001
PRECISION = 69


# ------- порошок уходи --------

mp.dps = PRECISION


@singleton
class GlobalConfig:
    FORCE_SOLVE_SYSTEM: bool = False

    def __init__(self) -> None:
        pass
