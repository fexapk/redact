import sys

from PySide6.QtWidgets import QApplication

from redact_app.logging_config import configure_logging
from redact_app.main_window import MainWindow


def main() -> int:
    """Start the desktop application."""
    configure_logging()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

