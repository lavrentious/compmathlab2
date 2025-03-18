from enum import Enum
from typing import List, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
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
from solvers.fixed_point_iteration_system_solver import FixedPointIterationSystemSolver
from solvers.system_solver import SystemSolver
from utils.equations import SYSTEM_PRESETS, MultivariableEquation
from utils.validation import is_float, to_float
from utils.writer import ResWriter

logger = GlobalLogger()


class SolutionMethod(Enum):
    FIXED_POINT_ITERATION = "Fixed point iteration"


class SystemTab(QWidget):
    result: Tuple[List[str], List[float], List[float], int] | None = None
    equations: List[MultivariableEquation] | None = None
    equation_inputs: List[QLineEdit]
    precision_input: QLineEdit
    method_combobox: QComboBox
    presets_combobox: QComboBox
    solve_button: QPushButton
    plot_button: QPushButton
    result_table: QTableWidget
    plot_container: PlotContainer
    equations_vbox: QVBoxLayout

    def __init__(self):
        super().__init__()
        grid0 = QGridLayout()

        vbox0 = QVBoxLayout()
        self.equation_inputs = []

        self.presets_combobox = QComboBox()
        for i, preset in enumerate(SYSTEM_PRESETS):
            self.presets_combobox.addItem(f"Preset {i+1}", userData=preset)
        self.presets_combobox.currentTextChanged.connect(self.load_preset)
        vbox0.addWidget(self.presets_combobox)

        vbox0.addWidget(QLabel("Equations:"))
        self.equations_vbox = QVBoxLayout()
        self.equations_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        vbox0.addLayout(self.equations_vbox)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.manual_plot)
        vbox0.addWidget(self.plot_button)

        self.precision_input = QLineEdit()
        self.precision_input.setPlaceholderText(f"default={EPS}")
        vbox0.addWidget(QLabel("Precision:"))
        vbox0.addWidget(self.precision_input)

        self.method_combobox = QComboBox()
        self.method_combobox.addItems([method.value for method in SolutionMethod])
        vbox0.addWidget(self.method_combobox)

        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve_equations)
        vbox0.addWidget(self.solve_button)

        grid0.addLayout(vbox0, 0, 0, 7, 1)
        vbox0.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid0.setRowStretch(0, 1)

        self.result_table = QTableWidget(3, 1)
        font = self.result_table.font()
        font.setFamily("Courier New")
        self.result_table.setFont(font)
        self.result_table.setVerticalHeaderLabels(["x", "f(x)", "iterations"])
        self.result_table.horizontalHeader().setVisible(False)
        self.result_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.result_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.result_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.result_table.horizontalHeader().setSectionResizeMode(
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
        grid0.addWidget(self.plot_container, 0, 1, 8, 1)

        grid0.setColumnStretch(1, 0)
        self.setLayout(grid0)

        self.set_equations(self.presets_combobox.itemData(0))

    def load_preset(self, text: str):
        logger.debug(f"Loading preset '{text}'")
        index = self.presets_combobox.findText(text)
        data = self.presets_combobox.itemData(index)
        system: List[MultivariableEquation] | None = data
        if system is None:
            logger.warning(f"Preset {text} ({index=}) is None")
            return

        logger.debug(f"Preset {text} ({index=}) loaded")
        self.set_equations(system)

    def set_equations(self, equations: List[MultivariableEquation]):
        self.equations = equations
        for equation_input in self.equation_inputs:
            self.equations_vbox.removeWidget(equation_input)
            equation_input.deleteLater()
        self.equation_inputs.clear()
        for e in equations:
            equation_input = QLineEdit(e.f_str())
            equation_input.setReadOnly(True)
            self.equation_inputs.append(equation_input)
            self.equations_vbox.addWidget(equation_input)

    def set_result(self, x: List[float], y: List[float], iterations: int):
        self.result = ([i.text() for i in self.equation_inputs], x, y, iterations)
        self.result_table.setItem(0, 0, QTableWidgetItem(str(x)))
        self.result_table.setItem(0, 1, QTableWidgetItem(str(y)))
        self.result_table.setItem(0, 2, QTableWidgetItem(str(iterations)))

    def _parse_values(
        self,
    ) -> Tuple[List[MultivariableEquation], float, SolutionMethod]:
        precision = self.precision_input.text()
        if not precision:
            precision = str(EPS)
        if not is_float(precision):
            raise ValueError("Precision is not a float")
        return (
            self.equations or [],
            to_float(precision),
            SolutionMethod(self.method_combobox.currentText()),
        )

    def parse_validate_plot(self):
        equations, precision, solution_method = self._parse_values()
        self.plot_container.canvas.plot_system(equations)
        return equations, precision, solution_method

    def manual_plot(self):
        logger.debug("plotting")
        try:
            self.parse_validate_plot()
        except ValueError as e:
            show_error_message(str(e))

    def solve_equations(self):
        try:
            fn_system, precision, solution_method = self.parse_validate_plot()
        except ValueError as e:
            show_error_message(str(e))
            return
        logger.debug("precision", precision)

        solver = SystemSolver()
        if solution_method == SolutionMethod.FIXED_POINT_ITERATION:
            logger.debug("using fixed point iteration")
            solver = FixedPointIterationSystemSolver()

        if not solver.check_convergence(fn_system):
            show_error_message("method does not converge")
            return
        try:
            res = solver.solve(fn_system, precision)
        except ValueError as e:
            show_error_message(str(e))
            return
        if not res:
            return
        xs, iterations = res
        self.set_result(xs, [fn.f(*xs) for fn in fn_system], iterations)
        if len(xs) == 2:
            self.plot_container.canvas.plot_point(*xs)

    def save_to_file(self):
        if not self.result:
            show_error_message("эээ баклан")
            return
        equation_str, x, y, iterations = self.result
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_path == "":
            return
        res_writer = ResWriter(open(file_path, "w"))
        res_writer.write(equation_str, x, y, iterations)
        res_writer.destroy()
