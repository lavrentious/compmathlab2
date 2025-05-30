from typing import Callable, Tuple

import numpy as np
import sympy as sp  # type: ignore
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
from utils.equations import Equation, SolutionMethod
from utils.math import check_single_root
from utils.validation import is_float, to_sp_float
from utils.writer import ResWriter, SolutionResult

logger = GlobalLogger()


class SingleTab(QWidget):
    result: SolutionResult | None = None
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

    def __init__(self) -> None:
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

        self.result_table = QTableWidget(3, 1)
        font = self.result_table.font()
        font.setFamily("Courier New")
        self.result_table.setFont(font)
        self.result_table.setVerticalHeaderLabels(["x", "f(x)", "iterations"])
        result_table_horizontal_header = self.result_table.horizontalHeader()
        if result_table_horizontal_header is not None:
            result_table_horizontal_header.setVisible(False)
            result_table_horizontal_header.setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
        self.result_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.result_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        result_table_vertical_header = self.result_table.verticalHeader()
        if result_table_vertical_header is not None:
            result_table_vertical_header.setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
        self.result_table.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
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

    def set_result(
        self,
        equation: Equation,
        x: sp.Float,
        y: sp.Float,
        iterations: int,
        solution_method: SolutionMethod,
    ) -> None:
        self.result = SolutionResult(equation, x, y, iterations, solution_method)
        self.result_table.setItem(0, 0, QTableWidgetItem(str(x)))
        self.result_table.setItem(1, 0, QTableWidgetItem(str(y)))
        self.result_table.setItem(2, 0, QTableWidgetItem(str(iterations)))

    def _parse_values(self) -> Tuple[str, sp.Float, sp.Float, sp.Float, SolutionMethod]:
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
            precision = str(EPS)
        if not is_float(interval_l):
            raise ValueError("Interval L is not a float")
        if not is_float(interval_r):
            raise ValueError("Interval R is not a float")
        if not is_float(precision):
            raise ValueError("Precision is not a float")
        return (
            equation,
            to_sp_float(interval_l),
            to_sp_float(interval_r),
            to_sp_float(precision),
            SolutionMethod(self.method_combobox.currentText()),
        )

    def parse_validate_plot(self) -> Tuple[Equation, sp.Float, SolutionMethod]:
        equation_str, interval_l, interval_r, precision, solution_method = (
            self._parse_values()
        )
        equation = Equation(interval_l, interval_r, equation_str=equation_str)
        self.plot_function(equation.f, equation.interval_l, equation.interval_r)
        return equation, precision, solution_method

    def manual_plot(self) -> None:
        try:
            self.parse_validate_plot()
        except ValueError as e:
            show_error_message(str(e))

    def save_to_file(self) -> None:
        if not self.result:
            show_error_message("эээ баклан")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Open File", "", "All Files (*)"
        )
        if not file_path:
            return
        res_writer = ResWriter(file_path)
        res_writer.write_solution(self.result)
        res_writer.destroy()

    def solve_equation(self) -> None:
        try:
            equation, precision, solution_method = self.parse_validate_plot()
        except ValueError as e:
            show_error_message(str(e))
            return
        logger.debug("interval", equation.interval_l, equation.interval_r)
        logger.debug("precision", precision)

        solver = Solver()
        if not check_single_root(equation.f, equation.interval_l, equation.interval_r):
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

        if not solver.check_convergence(equation):
            show_error_message("method does not converge")
            return
        try:
            res = solver.solve(equation, precision)
            if res is None:
                raise ValueError("method does not converge")
            x, iterations = res
            self.set_result(equation, x, equation.f(x), iterations, solution_method)
            self.plot_container.canvas.plot_point(x, equation.f(x))
        except Exception as e:
            show_error_message(str(e))
            return

    def plot_function(
        self, fn: Callable[[sp.Float], sp.Float], l: sp.Float, r: sp.Float
    ) -> None:
        w = r - l
        xs = np.linspace(l - w * 0.1, r + w * 0.1, 1000)
        ys = [fn(x) for x in xs]
        self.plot_container.canvas.clear()
        self.plot_container.canvas.plot_function(list(xs), ys, "f(x)")
        self.plot_container.canvas.highlight_x_interval(l, r)
