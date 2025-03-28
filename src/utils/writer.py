import json
import os
from enum import Enum
from io import TextIOWrapper
from typing import Any, List

# sympy has no types :(
import sympy as sp  # type: ignore

from logger import GlobalLogger
from utils.equations import Equation, EquationSystem, EquationSystemSolution

logger = GlobalLogger()


class FileFormat(Enum):
    JSON = "json"
    PLAIN = "plain"


class SolutionResult:
    equation: Equation
    x: sp.Float
    y: sp.Float
    iterations: int

    def __init__(self, equation: Equation, x: float, y: float, iterations: int):
        self.equation = equation
        self.x = x
        self.y = y
        self.iterations = iterations


class SystemSolutionResult:
    system: EquationSystem
    solution: EquationSystemSolution
    ys: List[float]
    iterations: int

    def __init__(
        self,
        system: EquationSystem,
        solution: EquationSystemSolution,
        ys: List[float],
        iterations: int,
    ):
        self.system = system
        self.solution = solution
        self.ys = ys
        self.iterations = iterations


class ResWriter:
    out_stream: TextIOWrapper | Any
    file_path: str | None = None

    def __init__(self, out_stream: TextIOWrapper | Any | str):
        if type(out_stream) == str:
            self.file_path = out_stream
            out_stream = self._get_out_stream(out_stream)
        self.out_stream = out_stream

    def _get_out_stream(self, file_path: str) -> TextIOWrapper | Any:
        if not file_path:
            raise ValueError("no file specified")
        if os.path.exists(file_path) and not os.access(
            os.path.dirname(file_path), os.W_OK
        ):
            raise PermissionError(f"no write permission for {file_path}")
        return open(file_path, "w")

    def write_solution(self, result: SolutionResult) -> None:
        if not self.file_path:
            raise ValueError("no file specified")
        file_ext = os.path.splitext(self.file_path)[1]
        res_writer: ResWriter = PlainWriter(self.out_stream)
        if file_ext == ".json":
            res_writer = JsonWriter(self.out_stream)
        logger.debug("using writer", res_writer.__class__.__name__)
        res_writer.write_solution(result)

    def write_system_solution(self, result: SystemSolutionResult) -> None:
        if not self.file_path:
            raise ValueError("no file specified")
        file_ext = os.path.splitext(self.file_path)[1]
        res_writer: ResWriter = PlainWriter(self.out_stream)
        if file_ext == ".json":
            res_writer = JsonWriter(self.out_stream)
        logger.debug("using writer", res_writer.__class__.__name__)
        res_writer.write_system_solution(result)

    def destroy(self) -> None:
        self.out_stream.close()


class PlainWriter(ResWriter):
    def write_solution(self, result: SolutionResult) -> None:
        self.out_stream.write(f"Equation: {result.equation.f_str()} = 0\n")
        self.out_stream.write(f"phi(x) = {result.equation.dphi_str()}\n")
        self.out_stream.write(f"f'(x) = {result.equation.df_str()}\n")
        self.out_stream.write(f"phi'(x) = {result.equation.dphi_str()}\n")
        self.out_stream.write(
            f"Interval: [{result.equation.interval_l}, {result.equation.interval_r}]\n"
        )
        self.out_stream.write(f"x: {result.x}\n")
        self.out_stream.write(f"y: {result.y}\n")
        self.out_stream.write(f"Iterations: {result.iterations}\n")
        self.out_stream.flush()

    def write_system_solution(self, result: SystemSolutionResult) -> None:
        self.out_stream.write(f"System:\n")
        for i in range(len(result.system.equations)):
            equation = result.system.equations[i]
            self.out_stream.write(f"{i+1}).\n")
            self.out_stream.write(f"    {equation.f_str()} = 0\n")
            self.out_stream.write(
                f"    phi: {str(equation.phi_lhs)} = {equation.phi_str()}\n"
            )
        self.out_stream.write(f"Solution: {result.solution}\n")
        self.out_stream.write(f"Iterations: {result.iterations}\n")
        self.out_stream.flush()


class JsonWriter(ResWriter):
    def write_solution(self, result: SolutionResult) -> None:

        obj = {
            "equation": result.equation.f_str(),
            "phi": result.equation.phi_str(),
            "f'": result.equation.df_str(),
            "phi'": result.equation.dphi_str(),
            "interval": [result.equation.interval_l, result.equation.interval_r],
            "x": str(result.x),
            "y": str(result.y),
            "iterations": result.iterations,
        }
        logger.debug("dumping json", obj)

        json.dump(
            obj,
            self.out_stream,
            indent=4,
        )
        self.out_stream.write("\n")
        self.out_stream.flush()

    def write_system_solution(self, result: SystemSolutionResult) -> None:

        obj = {
            "symbols": [str(s) for s in result.system.symbols],
            "system": [
                {
                    "f": equation.f_str(),
                    "phi_lhs": str(equation.phi_lhs),
                    "phi": equation.phi_str(),
                }
                for equation in result.system.equations
            ],
            "solution": {str(k): str(v) for k, v in result.solution.items()},
            "ys": [float(y) for y in result.ys],
            "iterations": result.iterations,
        }
        logger.debug("dumping json", obj)

        json.dump(
            obj,
            self.out_stream,
            indent=4,
        )
        self.out_stream.write("\n")
        self.out_stream.flush()
