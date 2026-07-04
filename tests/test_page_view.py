import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from redact_app.page_view import MAX_FIT_WIDTH_PAGE_WIDTH, PageView


def test_page_view_defaults_to_bounded_fit_width() -> None:
    app = QApplication.instance() or QApplication([])
    view = PageView()
    view.set_viewport_size(QSize(1920, 1000))
    view.set_page(0, Image.new("RGB", (1600, 2200), "white"), [])

    target = view._image_target_rect()

    assert view.fit_mode == "width"
    assert target.width() == MAX_FIT_WIDTH_PAGE_WIDTH
    assert target.left() > 0
    assert view.height() > 1000
    assert app is not None


def test_page_view_can_fit_entire_page() -> None:
    app = QApplication.instance() or QApplication([])
    view = PageView()
    view.set_viewport_size(QSize(1920, 1000))
    view.set_page(0, Image.new("RGB", (1600, 2200), "white"), [])

    view.set_fit_mode("page")
    target = view._image_target_rect()

    assert target.height() <= 1000
    assert target.width() < MAX_FIT_WIDTH_PAGE_WIDTH
    assert app is not None

