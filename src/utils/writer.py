import sys
from io import TextIOWrapper
from typing import Any

# sympy has no types :(
import sympy as sp  # type: ignore

from logger import GlobalLogger
from utils.equations import Equation

logger = GlobalLogger()


class ResWriter:
    out_stream: TextIOWrapper | Any

    def __init__(self, out_stream: TextIOWrapper | Any = sys.stdout):
        self.out_stream = out_stream

    def write(self, equation: Equation, x: float, y: float, iterations: int):
        self.out_stream.write(f"Equation: {equation.f_str()} = 0\n")
        self.out_stream.write(f"phi(x) = {equation.dphi_str()}\n")
        self.out_stream.write(f"f'(x) = {equation.df_str()}\n")
        self.out_stream.write(f"phi'(x) = {equation.dphi_str()}\n")
        self.out_stream.write(
            f"Interval: [{equation.interval_l}, {equation.interval_r}]\n"
        )
        self.out_stream.write(f"x: {x}\n")
        self.out_stream.write(f"y: {y}\n")
        self.out_stream.write(f"Iterations: {iterations}\n")
        self.out_stream.flush()

    def destroy(self):
        self.out_stream.close()
