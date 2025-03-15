from enum import Enum
from typing import Callable, Tuple

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import EPS
from gui.components.plot_container import PlotContainer
from gui.guiutils import show_error_message
from logger import GlobalLogger
from solvers.chord_solver import ChordSolver
from solvers.fixed_point_iteration_solver import FixedPointIterationSolver
from solvers.newton_solver import NewtonSolver
from solvers.solver import Solver
from utils import is_float, to_float, validate_and_parse_equation
from utils import ResWriter

logger = GlobalLogger()


class SolutionMethod(Enum):
    CHORD = "Chord"
    NEWTON = "Newton"
    FIXED_POINT_ITERATION = "Fixed point iteration"


class SingleTab(QWidget):
    result: Tuple[str, float, float, int] | None = None
    equation_input: QLineEdit
    interval_l_input: QLineEdit
    interval_r_input: QLineEdit
    precision_input: QLineEdit
    method_combobox: QComboBox
    solve_button: QPushButton
    plot_button: QPushButton
    result_table: QTableWidget
    plot_container: PlotContainer
    save_to_file_button: QPushButton

    def __init__(self):
        super().__init__()

        grid0 = QGridLayout()

        vbox0 = QVBoxLayout()
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("e.g. x**2 - 1")
        vbox0.addWidget(QLabel("Equation:"))
        vbox0.addWidget(self.equation_input)
        vbox0.addWidget(QLabel("Interval:"))
        hbox0 = QHBoxLayout()
        hbox0.addWidget(QLabel("L:"))
        self.interval_l_input = QLineEdit()
        hbox0.addWidget(self.interval_l_input)
        hbox0.addWidget(QLabel("R:"))
        self.interval_r_input = QLineEdit()
        hbox0.addWidget(self.interval_r_input)
        vbox0.addLayout(hbox0)
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.manual_plot)
        vbox0.addWidget(self.plot_button)
        vbox0.addWidget(QLabel("Precision:"))
        self.precision_input = QLineEdit()
        self.precision_input.setPlaceholderText(f"default={EPS}")
        vbox0.addWidget(self.precision_input)
        self.method_combobox = QComboBox()
        self.method_combobox.addItems([method.value for method in SolutionMethod])
        vbox0.addWidget(self.method_combobox)
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve_equation)
        vbox0.addWidget(self.solve_button)
        # vbox0.addStretch()
        grid0.addLayout(vbox0, 0, 0, 7, 1)
        vbox0.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid0.setRowStretch(0, 1)

        self.result_table = QTableWidget(1, 3)
        self.result_table.setHorizontalHeaderLabels(["x", "f(x)", "iterations"])
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.result_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.result_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.result_table.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        self.result_table.setFixedHeight(50)
        grid0.addWidget(self.result_table, 6, 0, 1, 1)

        self.save_to_file_button = QPushButton("Save to file")
        self.save_to_file_button.clicked.connect(self.save_to_file)
        grid0.addWidget(self.save_to_file_button, 7, 0, 1, 1)

        self.plot_container = PlotContainer()
        self.plot_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # grid0.addWidget(self.plot_canvas, 0, 1, 8, 1)
        grid0.addWidget(self.plot_container, 0, 1, 8, 1)

        grid0.setColumnStretch(1, 0)
        self.setLayout(grid0)

    def set_result(self, x: float, y: float, iterations: int):
        self.result = (self.equation_input.text(), x, y, iterations)
        self.result_table.setItem(0, 0, QTableWidgetItem(str(x)))
        self.result_table.setItem(0, 1, QTableWidgetItem(str(y)))
        self.result_table.setItem(0, 2, QTableWidgetItem(str(iterations)))

    def _parse_values(self) -> Tuple[str, float, float, float, SolutionMethod]:
        equation = self.equation_input.text()
        interval_l = self.interval_l_input.text()
        interval_r = self.interval_r_input.text()
        precision = self.precision_input.text()
        if not equation:
            raise ValueError("Equation is empty")
        if not interval_l:
            raise ValueError("Interval L is empty")
        if not interval_r:
            raise ValueError("Interval R is empty")
        if not precision:
            precision = EPS
        if not is_float(interval_l):
            raise ValueError("Interval L is not a float")
        if not is_float(interval_r):
            raise ValueError("Interval R is not a float")
        if not is_float(precision):
            raise ValueError("Precision is not a float")
        return (
            equation,
            to_float(interval_l),
            to_float(interval_r),
            to_float(precision),
            SolutionMethod(self.method_combobox.currentText()),
        )

    def parse_validate_plot(self):
        equation, interval_l, interval_r, precision, solution_method = (
            self._parse_values()
        )
        fn = validate_and_parse_equation(equation)
        self.plot_function(fn, interval_l, interval_r)
        return fn, interval_l, interval_r, precision, solution_method

    def manual_plot(self):
        try:
            self.parse_validate_plot()
        except ValueError as e:
            show_error_message(str(e))

    def save_to_file(self):
        if not self.result:
            show_error_message("эээ баклан")
            return
        equation_str, x, y, iterations = self.result
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Open File", "", "All Files (*)"
        )
        res_writer = ResWriter(open(file_path, "w"))
        res_writer.write(equation_str, x, y, iterations)
        res_writer.destroy()

    def solve_equation(self):
        try:
            fn, interval_l, interval_r, precision, solution_method = (
                self.parse_validate_plot()
            )
        except ValueError as e:
            show_error_message(str(e))
            return
        logger.debug("interval", interval_l, interval_r)
        logger.debug("precision", precision)

        solver = Solver()
        if not solver.check_single_root(fn, interval_l, interval_r):
            show_error_message("there is not exactly 1 root in the interval")
            return

        if solution_method == SolutionMethod.CHORD:
            logger.debug("using chord")
            solver = ChordSolver()
        elif solution_method == SolutionMethod.NEWTON:
            logger.debug("using newton")
            solver = NewtonSolver()
        elif solution_method == SolutionMethod.FIXED_POINT_ITERATION:
            logger.debug("using fixed point iteration")
            solver = FixedPointIterationSolver()

        if not solver.check_convergence(fn, interval_l, interval_r):
            show_error_message("method does not converge")
            return
        res = solver.solve(fn, interval_l, interval_r, precision)
        if res:
            x, iterations = res
            self.set_result(x, fn(x), iterations)

    def plot_function(self, fn: Callable[[float], float], l: float, r: float):
        w = r - l
        xs = np.linspace(l - w * 0.1, r + w * 0.1, 1000)
        ys = [fn(x) for x in xs]
        self.plot_container.canvas.clear()
        self.plot_container.canvas.plot_function(xs, ys, "f(x)")
        self.plot_container.canvas.highlight_x_interval(l, r)
