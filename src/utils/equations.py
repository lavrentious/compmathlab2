from typing import Callable


class Equation:
    equation_str: str
    f: Callable[[float], float]
    # x = phi(x)
    phi_str: str
    phi: Callable[[float], float]

    df: Callable[[float], float] | None
    dphi: Callable[[float], float] | None

    def __init__(
        self,
        equation_str: str,
        f: Callable[[float], float],
        phi_str: str | None = None,
        phi: Callable[[float], float] | None = None,
        df: Callable[[float], float] | None = None,
        dphi: Callable[[float], float] | None = None,
    ):
        self.equation_str = equation_str
        self.f = f
        if phi_str:
            self.phi_str = phi_str
        if phi is not None:
            self.phi = phi
        else:
            self.phi = lambda x: x
        self.df = df
        self.dphi = dphi
