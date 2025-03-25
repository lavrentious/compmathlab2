from utils.meta import singleton


EPS = 0.0001


@singleton # type: ignore
class GlobalConfig:
    FORCE_SOLVE_SYSTEM: bool = False

    def __init__(self) -> None:
        pass
