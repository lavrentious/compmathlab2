from PyQt6.QtWidgets import QInputDialog, QMessageBox


def show_error_message(
    message: str, informative_text: str | None = None, window_title: str = "Error"
):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(window_title)
    msg.setText(message)
    if informative_text is not None:
        msg.setInformativeText(informative_text)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def open_input_dialog(parent, title: str, message: str):
    text, ok = QInputDialog.getText(parent, title, message)
    if ok:
        return text
