from PyQt6.QtWidgets import QInputDialog, QMessageBox, QWidget


def show_error_message(
    message: str, informative_text: str | None = None, window_title: str = "Error"
) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(window_title)
    msg.setText(message)
    if informative_text is not None:
        msg.setInformativeText(informative_text)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def open_input_dialog(parent: QWidget, title: str, message: str) -> str | None:
    text, ok = QInputDialog.getText(parent, title, message)
    if ok:
        return text
    return None
