import math
import sympy as sp  # type: ignore
import re
from logger import GlobalLogger
from utils.math import get_phi_with_lambda
from utils.math import df as _df
from utils.math import d2f as _d2f

logger = GlobalLogger()


class Equation:
    # f(x) = 0
    f: sp.Lambda
    df: sp.Lambda
    d2f: sp.Lambda

    # x = phi(x)
    phi: sp.Lambda
    dphi: sp.Lambda

    interval_l: float
    interval_r: float

    def __init__(
        self,
        interval_l: float,
        interval_r: float,
        equation_str: str | None = None,
        f: sp.Lambda | None = None,
        phi: sp.Lambda | None = None,
    ):
        """
        supported variants:
        1. Equation(interval_l, interval_r, f=)
        2. Equation(interval_l, interval_r, f=, phi=)
        3. Equation(interval_r, interval_r, equation_str=)
        """
        if f is not None:
            pass
        elif equation_str is not None:
            f = self._validate_and_parse_equation(equation_str)
        else:
            raise ValueError("either equation_str or f must be provided")
        if phi is None:
            phi, dphi = get_phi_with_lambda(f, interval_l, interval_r)
        self.f = f
        self.phi = phi
        try:
            self.df = sp.Lambda(sp.symbols("x"), sp.diff(f.expr, sp.symbols("x")))
        except sp.SympifyError as e:
            logger.warning(
                f"sympy could not differentiate {self.f_str()}, {interval_l=}, {interval_r=}; falling back to stupid differentiation\n{e}"
            )
            self.df = sp.Lambda(sp.symbols("x"), lambda x: _df(f, x))
        try:
            self.d2f = sp.Lambda(sp.symbols("x"), sp.diff(self.df.expr, sp.symbols("x")))
        except sp.SympifyError as e:
            logger.warning(
                f"sympy could not differentiate {self.df_str()}, {interval_l=}, {interval_r=} (second derivative); falling back to stupid differentiation\n{e}"
            )
            self.d2f = sp.Lambda(sp.symbols("x"), lambda x: _d2f(self.df, x))
        if dphi is None:
            dphi = sp.Lambda(sp.symbols("x"), sp.diff(phi, sp.symbols("x")))
        self.dphi = dphi
        self.interval_l = interval_l
        self.interval_r = interval_r

    def f_str(self):
        return str(self.f.expr)

    def phi_str(self):
        return str(self.phi.expr)

    def df_str(self):
        return str(self.df.expr)

    def dphi_str(self):
        return str(self.dphi.expr)

    def _validate_and_parse_equation(self, equation_str: str) -> sp.Lambda:
        equation_str = equation_str.replace(",", ".").replace("^", "**")
        allowed_functions = (
            "("
            + "|".join(
                filter(
                    lambda s: not s.startswith("_")
                    and not s.endswith("_")
                    and s not in {"inf", "nan"},
                    math.__dict__.keys(),
                )
            )
            + ")"
        )
        allowed_pattern = r"^[0-9+\-*/().^ \s" + allowed_functions + "]+$"
        if not re.match(allowed_pattern, equation_str):
            raise ValueError("Invalid characters in the equation")
        x = sp.symbols("x")
        try:
            expr = sp.sympify(equation_str)
        except sp.SympifyError:
            raise ValueError("Invalid equation format")
        used_symbols = expr.free_symbols
        if len(used_symbols) > 1:
            raise ValueError(
                f"Invalid variable(s) {used_symbols - {x}} in the equation. Only 'x' is allowed."
            )
        logger.debug("parsed expression", expr)
        func = sp.Lambda(x, expr)
        return func
