from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from gui.views.single_tab import SingleTab
from gui.views.system_tab import SystemTab


class EquationSolverApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("pupka zalupka v1.0")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        tab_widget = QTabWidget()
        tab_widget.addTab(SingleTab(), "Single")
        tab_widget.addTab(SystemTab(), "System")
        layout.addWidget(tab_widget)

        central_widget.setLayout(layout)
