from typing import Callable

import numpy as np
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from gui.components.plot_canvas import PlotCanvas

X_POINTS_PER_PLOT = 1000


class PlotContainer(QWidget):
    toolbar: NavigationToolbar2QT
    canvas: PlotCanvas
    interval_l: float
    interval_r: float
    fn: Callable[[float], float]

    def __init__(self):
        super().__init__()
        self.canvas = PlotCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # self.canvas.ax.callbacks.connect("xlim_changed", replot_fn) # TODO

    def replot_fn(self, event_ax):
        x_min, x_max = self.ax.get_xlim()
        new_x = np.linspace(x_min, x_max, X_POINTS_PER_PLOT)
        new_y = [self.fn(x) for x in new_x]

        self.line.set_data(new_x, new_y)
        self.canvas.draw()

    def set_fn(
        self, fn: Callable[[float], float], interval_l: float, interval_r: float
    ):
        self.fn = fn
        self.interval_l = interval_l
        self.interval_r = interval_r
