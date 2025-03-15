from typing import List

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas


class PlotCanvas(FigureCanvas):
    figure: plt.Figure
    ax: plt.Axes

    def __init__(self):
        self.figure, self.ax = plt.subplots()
        super().__init__(self.figure)
        self.ax.autoscale(False)

    def clear(self):
        self.ax.clear()

    def plot_function(self, x_vals: List[float], y_vals: List[float], label: str):
        self.ax.plot(x_vals, y_vals, label=label)
        self.ax.axhline(0, color="gray", lw=0.5)
        self.ax.axvline(0, color="gray", lw=0.5)
        self.ax.grid(True)
        self.ax.legend()
        self.draw()

    def highlight_x_interval(self, l: float, r: float):
        self.ax.axvspan(
            l, r, facecolor="yellow", alpha=0.5, label="selected x interval"
        )
        self.ax.legend()
        self.draw()
