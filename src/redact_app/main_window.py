from PySide6.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):
    """Main application window.

    The full PDF viewer and redaction controls are implemented in later
    milestones. This placeholder keeps the application entrypoint runnable
    while the project skeleton is established.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Redact")
        self.resize(1000, 800)
        self.setCentralWidget(QLabel("Redact PDF app skeleton"))

