import os
import sys

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication

from argparser import ArgParser
from gui.gui import EquationSolverApp
from logger import GlobalLogger, Logger, LogLevel

if __name__ != "__main__":
    exit(0)


def run() -> None:
    parser = ArgParser()
    logger = Logger()
    parser.parse_and_validate_args(logger)
    GlobalLogger().set_min_level(LogLevel.DEBUG if parser.verbose else LogLevel.INFO)
    GlobalLogger().debug("Verbose mode:", parser.verbose)

    if parser.help_mode:
        parser.print_help()
        return

    app = QApplication(sys.argv)
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.abspath(os.path.join(scriptDir, "..", "assets", "icon.png"))
    app.setWindowIcon(QtGui.QIcon(path))
    window = EquationSolverApp()
    window.show()
    sys.exit(app.exec())


run()
