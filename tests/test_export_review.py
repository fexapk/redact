import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from redact_app.main_window import MainWindow


def test_opened_page_counts_as_reviewed() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._document = SimpleNamespace(page_count=3)
    window._page_index = 0

    window._mark_current_page_visited()

    assert window._visited_pages == {0}
    assert window._unvisited_page_numbers() == [2, 3]
    assert window._review_progress_text() == "Reviewed 1 / 3 pages"
    assert app is not None


def test_unvisited_page_numbers_use_human_page_numbers() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._document = SimpleNamespace(page_count=4)
    window._visited_pages = {0, 2}

    assert window._unvisited_page_numbers() == [2, 4]
    assert app is not None


def test_single_page_document_is_reviewed_after_first_render() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._document = SimpleNamespace(page_count=1)
    window._page_index = 0

    window._mark_current_page_visited()

    assert window._unvisited_page_numbers() == []
    assert window._review_progress_text() == "Reviewed 1 / 1 pages"
    assert app is not None

