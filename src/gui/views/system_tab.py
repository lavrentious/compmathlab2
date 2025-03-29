from typing import Dict, List, Tuple

import sympy as sp  # type: ignore
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

from config import EPS, GlobalConfig
from gui.components.plot_container import PlotContainer
from gui.guiutils import show_error_message
from logger import GlobalLogger
from solvers.fixed_point_iteration_system_solver import FixedPointIterationSystemSolver
from solvers.system_solver import SystemSolver
from utils.equations import (
    SYSTEM_PRESETS,
    EquationSystem,
    EquationSystemSolution,
    SystemSolutionMethod,
)
from utils.validation import is_float, to_sp_float
from utils.writer import ResWriter, SystemSolutionResult

logger = GlobalLogger()


class SystemTab(QWidget):
    result: SystemSolutionResult | None = None
    equation_system: EquationSystem | None = None
    equation_inputs: List[QLineEdit]
    starting_xs_inputs: Dict[str, QLineEdit]
    starting_xs_vbox: QVBoxLayout
    precision_input: QLineEdit
    method_combobox: QComboBox
    presets_combobox: QComboBox
    solve_button: QPushButton
    plot_button: QPushButton
    result_table: QTableWidget
    plot_container: PlotContainer
    equations_vbox: QVBoxLayout

    def __init__(self) -> None:
        super().__init__()
        grid0 = QGridLayout()

        vbox0 = QVBoxLayout()
        self.equation_inputs = []
        self.starting_xs_inputs = {}

        self.presets_combobox = QComboBox()
        for i, preset in enumerate(SYSTEM_PRESETS):
            self.presets_combobox.addItem(f"Preset {i+1}", userData=preset)
        self.presets_combobox.currentTextChanged.connect(self.load_preset)
        vbox0.addWidget(self.presets_combobox)

        vbox0.addWidget(QLabel("Equations:"))
        self.equations_vbox = QVBoxLayout()
        self.equations_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        vbox0.addLayout(self.equations_vbox)

        vbox0.addWidget(QLabel("Starting Xs:"))
        self.starting_xs_vbox = QVBoxLayout()
        self.starting_xs_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        vbox0.addLayout(self.starting_xs_vbox)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.manual_plot)
        vbox0.addWidget(self.plot_button)

        self.precision_input = QLineEdit()
        self.precision_input.setPlaceholderText(f"default={EPS}")
        vbox0.addWidget(QLabel("Precision:"))
        vbox0.addWidget(self.precision_input)

        self.method_combobox = QComboBox()
        self.method_combobox.addItems([method.value for method in SystemSolutionMethod])
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
        result_table_horizontal_header = self.result_table.horizontalHeader()
        if result_table_horizontal_header is not None:
            result_table_horizontal_header.setVisible(False)
            result_table_horizontal_header.setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
        result_table_vertical_header = self.result_table.verticalHeader()
        if result_table_vertical_header is not None:
            result_table_vertical_header.setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
        self.result_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.result_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
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

        self.set_system(self.presets_combobox.itemData(0))

    def load_preset(self, text: str) -> None:
        logger.debug(f"Loading preset '{text}'")
        index = self.presets_combobox.findText(text)
        data = self.presets_combobox.itemData(index)
        system: EquationSystem | None = data
        if system is None:
            logger.warning(f"Preset {text} ({index=}) is None")
            return

        logger.debug(f"Preset {text} ({index=}) loaded")
        self.set_system(system)

    def set_system(self, system: EquationSystem) -> None:
        self.equation_system = system
        for equation_input in self.equation_inputs:
            self.equations_vbox.removeWidget(equation_input)
            equation_input.deleteLater()
        for [symbol, starting_point_input] in self.starting_xs_inputs.items():
            self.starting_xs_vbox.removeWidget(starting_point_input)
            starting_point_input.deleteLater()

        self.equation_inputs.clear()
        self.starting_xs_inputs.clear()
        for e in system.equations:
            equation_input = QLineEdit(e.f_str())
            equation_input.setReadOnly(True)
            self.equation_inputs.append(equation_input)
            self.equations_vbox.addWidget(equation_input)

        for symbol in sorted(system.symbols, key=str):
            starting_point_input = QLineEdit()
            starting_point_input.setPlaceholderText(f"{symbol}=")
            self.starting_xs_inputs[str(symbol)] = starting_point_input
            self.starting_xs_vbox.addWidget(starting_point_input)

        self.plot_container.canvas.clear()
        if len(system.symbols) == 2:
            self.plot_container.canvas.set_x_y_symbols(
                *sorted(map(str, system.symbols))
            )

    def set_result(
        self,
        xs: EquationSystemSolution,
        ys: List[sp.Float],
        iterations: int,
        solution_method: SystemSolutionMethod,
    ) -> None:
        if self.equation_system is None:
            return
        self.result = SystemSolutionResult(
            self.equation_system, xs, ys, iterations, solution_method
        )
        self.result_table.setItem(0, 0, QTableWidgetItem(str(xs)))
        self.result_table.setItem(0, 1, QTableWidgetItem(str(ys)))
        self.result_table.setItem(0, 2, QTableWidgetItem(str(iterations)))

    def _parse_validate_system(self) -> EquationSystem | None:
        return self.equation_system

    def _parse_validate_starting_xs(self) -> Dict[str, sp.Float]:
        for symbol, starting_point_input in self.starting_xs_inputs.items():
            if not starting_point_input.text():
                raise ValueError(f"Starting point for {symbol} is empty")
            if not is_float(starting_point_input.text()):
                raise ValueError(f"Starting point for {symbol} is not a float")
        return {
            symbol: to_sp_float(starting_point_input.text())
            for symbol, starting_point_input in self.starting_xs_inputs.items()
        }

    def _parse_validate_values(
        self,
    ) -> Tuple[
        EquationSystem | None, sp.Float, SystemSolutionMethod, Dict[str, sp.Float]
    ]:
        system = self._parse_validate_system()
        starting_xs = self._parse_validate_starting_xs()
        precision = self.precision_input.text()
        if not precision:
            precision = str(EPS)
        if not is_float(precision):
            raise ValueError("Precision is not a float")

        return (
            system,
            to_sp_float(precision),
            SystemSolutionMethod(self.method_combobox.currentText()),
            starting_xs,
        )

    def parse_validate_plot(
        self,
    ) -> Tuple[EquationSystem, sp.Float, SystemSolutionMethod, Dict[str, sp.Float]]:
        system, precision, solution_method, starting_xs = self._parse_validate_values()
        if system is None:
            raise ValueError("Equation system could not be parsed")
        self.plot_container.canvas.plot_system(system)
        self.plot_container.canvas.plot_point_multi(starting_xs)
        return system, precision, solution_method, starting_xs

    def manual_plot(self) -> None:
        logger.debug("plotting")
        try:
            system = self._parse_validate_system()
            if system is None:
                raise ValueError("Equation system could not be parsed")
            self.plot_container.canvas.plot_system(system)
        except ValueError as e:
            show_error_message(str(e))

        try:
            starting_xs = self._parse_validate_starting_xs()
            self.plot_container.canvas.plot_point_multi(starting_xs)
        except ValueError:
            pass

    def solve_equations(self) -> None:
        try:
            system, precision, solution_method, starting_xs = self.parse_validate_plot()
        except ValueError as e:
            show_error_message(str(e))
            return
        logger.debug("precision", precision)

        solver = SystemSolver()
        if solution_method == SystemSolutionMethod.FIXED_POINT_ITERATION:
            logger.debug("using fixed point iteration")
            solver = FixedPointIterationSystemSolver()

        if not solver.check_convergence(system, starting_xs):
            show_error_message("method does not converge")
            if GlobalConfig().FORCE_SOLVE_SYSTEM:
                logger.warning("system is non convergent, force solving due to flag")
            else:
                return
        try:
            self.plot_container.canvas.start_polygon_chain()
            self.plot_container.canvas.add_to_polygon_chain(starting_xs)
            res = solver.solve(system, starting_xs, precision, self._plot_iteration)
            self.plot_container.canvas.end_polygon_chain()
        except Exception as e:
            show_error_message(str(e))
            return
        if not res:
            return
        xs, iterations = res
        logger.debug(f"solution success, {xs=}, {iterations=}")
        self.set_result(xs, system.apply(xs), iterations, solution_method)
        if len(xs) == 2:
            self.plot_container.canvas.plot_point(*[xs[sym] for sym in xs.keys()])

    def _plot_iteration(self, xs: EquationSystemSolution, iteration: int) -> None:
        # logger.debug(f"plot iteration {iteration=} {xs=}")
        self.plot_container.canvas.add_to_polygon_chain(
            {str(k): v for k, v in xs.items()}
        )

    def save_to_file(self) -> None:
        if not self.result:
            show_error_message("эээ баклан")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_path == "":
            return
        res_writer = ResWriter(file_path)
        res_writer.write_system_solution(self.result)
        res_writer.destroy()
