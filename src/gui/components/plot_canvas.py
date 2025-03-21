from typing import List

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp  # type: ignore
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from logger import GlobalLogger
from utils.equations import EquationSystem

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # type: ignore # isort: skip


logger = GlobalLogger()


class PlotCanvas(FigureCanvas):
    figure: Figure
    ax: Axes

    def __init__(self) -> None:
        self.figure, self.ax = plt.subplots()
        super().__init__(self.figure)
        self.ax.autoscale(False)

    def clear(self) -> None:
        self.ax.clear()

    def plot_function(
        self, x_vals: List[float], y_vals: List[float], label: str
    ) -> None:
        self.ax.plot(x_vals, y_vals, label=label)
        self.ax.axhline(0, color="gray", lw=0.5)
        self.ax.axvline(0, color="gray", lw=0.5)
        self.ax.grid(True)
        self.ax.legend()
        self.draw()

    def highlight_x_interval(self, l: float, r: float) -> None:
        self.ax.axvspan(
            l, r, facecolor="yellow", alpha=0.5, label="selected x interval"
        )
        self.ax.legend()
        self.draw()

    def plot_system(self, system: EquationSystem) -> None:
        if len(system.symbols) > 2:
            return
        self.clear()
        self.ax.grid(True)
        self.ax.axhline(0, color="gray", lw=0.5)
        self.ax.axvline(0, color="gray", lw=0.5)
        if len(system.symbols) == 1:
            for e in system.equations:
                logger.debug(e, e.f.expr, e.f.expr.free_symbols)
                xs = list(np.linspace(-10, 10, 1000).astype(float))
                ys = [e.f(x) for x in xs]
                self.plot_function(xs, ys, "f(x)")
        elif len(system.symbols) == 2:
            x, y = system.symbols
            for e in system.equations:
                fn_np = sp.lambdify((x, y), e.f(x, y), "numpy")
                xs = list(np.linspace(-10, 10, 400).astype(float))
                ys = list(np.linspace(-10, 10, 400).astype(float))
                X, Y = np.meshgrid(xs, ys)
                Z = fn_np(X, Y)
                self.ax.contour(X, Y, Z, levels=[0], colors="r")
            self.ax.set_xlabel(x.name)
            self.ax.set_ylabel(y.name)
            self.draw()

    def plot_point(self, x: float, y: float) -> None:
        logger.debug(f"plotting point ({x}, {y})")
        self.ax.plot(x, y, marker="o", markersize=5)
        self.draw()
