from __future__ import annotations

import logging
from typing import Optional

from PIL import Image
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from redact_app.redaction import RedactionRect


logger = logging.getLogger(__name__)


class PageView(QWidget):
    """Widget that displays one rasterized PDF page and redaction rectangles."""

    redaction_created = Signal(RedactionRect)
    selection_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._page_index = 0
        self._image: Optional[QImage] = None
        self._image_size: tuple[int, int] = (0, 0)
        self._rectangles: list[RedactionRect] = []
        self._selected: Optional[RedactionRect] = None
        self._drag_start: Optional[QPoint] = None
        self._drag_current: Optional[QPoint] = None

    @property
    def selected_redaction(self) -> Optional[RedactionRect]:
        return self._selected

    def set_page(
        self,
        page_index: int,
        image: Image.Image,
        rectangles: list[RedactionRect],
    ) -> None:
        self._page_index = page_index
        self._image = _pil_image_to_qimage(image)
        self._image_size = image.size
        self._rectangles = rectangles
        self._selected = None
        self._drag_start = None
        self._drag_current = None
        self.selection_changed.emit(None)
        self.update()

    def set_rectangles(self, rectangles: list[RedactionRect]) -> None:
        self._rectangles = rectangles
        if self._selected not in rectangles:
            self._selected = None
            self.selection_changed.emit(None)
        self.update()

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(42, 42, 42))

        if self._image is None:
            painter.setPen(QColor(220, 220, 220))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Open a PDF")
            return

        target = self._image_target_rect()
        painter.fillRect(target.adjusted(-1, -1, 1, 1), QColor(235, 235, 235))
        painter.drawImage(target, self._image)

        for rect in self._rectangles:
            screen_rect = self._image_rect_to_screen(rect)
            painter.fillRect(screen_rect, QColor(0, 0, 0))
            if rect == self._selected:
                painter.setPen(QPen(QColor(45, 150, 255), 2))
                painter.drawRect(screen_rect)

        if self._drag_start and self._drag_current:
            drag_rect = QRect(self._drag_start, self._drag_current).normalized()
            painter.fillRect(drag_rect, QColor(0, 0, 0, 180))
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawRect(drag_rect)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._image is None:
            return

        image_point = self._screen_to_image_point(event.pos())
        if image_point is None:
            self._set_selected(None)
            return

        for rect in reversed(self._rectangles):
            if rect.contains(image_point.x(), image_point.y()):
                self._set_selected(rect)
                return

        self._set_selected(None)
        self._drag_start = event.pos()
        self._drag_current = event.pos()
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_start is None:
            return
        self._drag_current = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._drag_start is None:
            return

        start = self._screen_to_image_point(self._drag_start)
        end = self._screen_to_image_point(event.pos())
        self._drag_start = None
        self._drag_current = None

        if start is None or end is None:
            self.update()
            return

        rect = RedactionRect.from_points(
            self._page_index,
            start.x(),
            start.y(),
            end.x(),
            end.y(),
        ).clipped(*self._image_size)

        if rect.width >= 3 and rect.height >= 3:
            logger.info(
                "Created redaction page=%s x=%s y=%s width=%s height=%s",
                rect.page_index,
                rect.x,
                rect.y,
                rect.width,
                rect.height,
            )
            self.redaction_created.emit(rect)

        self.update()

    def _set_selected(self, rect: Optional[RedactionRect]) -> None:
        if self._selected == rect:
            return
        self._selected = rect
        self.selection_changed.emit(rect)
        self.update()

    def _image_target_rect(self) -> QRect:
        image_width, image_height = self._image_size
        if image_width == 0 or image_height == 0:
            return QRect()

        margin = 20
        available_width = max(1, self.width() - margin * 2)
        available_height = max(1, self.height() - margin * 2)
        scale = min(available_width / image_width, available_height / image_height)
        target_width = round(image_width * scale)
        target_height = round(image_height * scale)
        left = (self.width() - target_width) // 2
        top = (self.height() - target_height) // 2
        return QRect(left, top, target_width, target_height)

    def _screen_to_image_point(self, point: QPoint) -> Optional[QPoint]:
        target = self._image_target_rect()
        if not target.contains(point):
            return None

        image_width, image_height = self._image_size
        x = round((point.x() - target.left()) * image_width / target.width())
        y = round((point.y() - target.top()) * image_height / target.height())
        return QPoint(
            max(0, min(x, image_width)),
            max(0, min(y, image_height)),
        )

    def _image_rect_to_screen(self, rect: RedactionRect) -> QRect:
        target = self._image_target_rect()
        image_width, image_height = self._image_size
        left = round(target.left() + rect.x * target.width() / image_width)
        top = round(target.top() + rect.y * target.height() / image_height)
        right = round(target.left() + rect.right * target.width() / image_width)
        bottom = round(target.top() + rect.bottom * target.height() / image_height)
        return QRect(left, top, right - left, bottom - top)


def _pil_image_to_qimage(image: Image.Image) -> QImage:
    rgb = image.convert("RGB")
    data = rgb.tobytes("raw", "RGB")
    qimage = QImage(data, rgb.width, rgb.height, rgb.width * 3, QImage.Format.Format_RGB888)
    return qimage.copy()

