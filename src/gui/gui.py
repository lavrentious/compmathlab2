from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from gui.views.single_tab import SingleTab
from gui.views.system_tab import SystemTab


class EquationSolverApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("pupka zalupka v1.0")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget for QMainWindow
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()

        # Create tabs
        tab_widget = QTabWidget()
        tab_widget.addTab(SingleTab(), "Single")
        tab_widget.addTab(SystemTab(), "System")
        layout.addWidget(tab_widget)

        # Set layout for the central widget
        central_widget.setLayout(layout)

    def solve_equation(self):
        print("solving equation", self.equation_input.text())

    #     equation_str = self.equation_input.text()
    #     x = sp.symbols("x")
    #     equation = sp.sympify(equation_str)

    #     # Solve for roots
    #     roots = sp.solve(equation, x)
    #     self.result_label.setText(f"Roots: {roots}")

    #     # Plot the function
    #     self.ax.clear()
    #     f = sp.lambdify(x, equation, "numpy")
    #     x_vals = np.linspace(-10, 10, 1000)
    #     y_vals = f(x_vals)
    #     self.ax.plot(x_vals, y_vals, label=equation_str)
    #     self.ax.axhline(0, color="gray", lw=0.5)
    #     self.ax.axvline(0, color="gray", lw=0.5)
    #     self.ax.grid(True)
    #     self.ax.legend()
    #     self.canvas.draw()
