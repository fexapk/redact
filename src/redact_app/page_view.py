from __future__ import annotations

import logging
from typing import Optional

from PIL import Image
from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QScrollArea, QWidget

from redact_app.redaction import RedactionRect


logger = logging.getLogger(__name__)

VIEW_PADDING = 32
FIT_WIDTH_SIDE_PADDING = 80
MAX_FIT_WIDTH_PAGE_WIDTH = 1200


class PageScrollArea(QScrollArea):
    """Scroll container that keeps the page view sized for the viewport."""

    def __init__(self, page_view: "PageView") -> None:
        super().__init__()
        self._page_view = page_view
        self.setWidget(page_view)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.setBackgroundRole(self.backgroundRole())
        self.setFrameShape(QScrollArea.Shape.NoFrame)

    def resizeEvent(self, event: object) -> None:
        super().resizeEvent(event)
        self._page_view.set_viewport_size(self.viewport().size())


class PageView(QWidget):
    """Widget that displays one rasterized PDF page and redaction rectangles."""

    redaction_created = Signal(RedactionRect)
    selection_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._fit_mode = "width"
        self._viewport_size = QSize(640, 480)
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

    @property
    def fit_mode(self) -> str:
        return self._fit_mode

    def set_fit_mode(self, fit_mode: str) -> None:
        if fit_mode not in {"width", "page"}:
            raise ValueError(f"Unsupported fit mode: {fit_mode}")
        if self._fit_mode == fit_mode:
            return
        self._fit_mode = fit_mode
        logger.info("Changed viewer fit mode mode=%s", fit_mode)
        self._update_widget_size()

    def set_viewport_size(self, size: QSize) -> None:
        if self._viewport_size == size:
            return
        self._viewport_size = size
        self._update_widget_size()

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
        self._update_widget_size()

    def set_rectangles(self, rectangles: list[RedactionRect]) -> None:
        self._rectangles = rectangles
        if self._selected not in rectangles:
            self._selected = None
            self.selection_changed.emit(None)
        self.update()

    def sizeHint(self) -> QSize:
        return self._desired_widget_size()

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

        scale = self._display_scale()
        target_width = round(image_width * scale)
        target_height = round(image_height * scale)
        left = (self.width() - target_width) // 2
        top = VIEW_PADDING if self._fit_mode == "width" else (self.height() - target_height) // 2
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

    def _update_widget_size(self) -> None:
        self.setFixedSize(self._desired_widget_size())
        self.updateGeometry()
        self.update()

    def _desired_widget_size(self) -> QSize:
        if self._image is None:
            return self._viewport_size.expandedTo(QSize(640, 480))

        image_width, image_height = self._image_size
        scale = self._display_scale()
        target_width = round(image_width * scale)
        target_height = round(image_height * scale)

        if self._fit_mode == "width":
            width = max(self._viewport_size.width(), target_width + FIT_WIDTH_SIDE_PADDING * 2)
            height = target_height + VIEW_PADDING * 2
            return QSize(width, height)

        return self._viewport_size.expandedTo(
            QSize(target_width + VIEW_PADDING * 2, target_height + VIEW_PADDING * 2)
        )

    def _display_scale(self) -> float:
        image_width, image_height = self._image_size
        if image_width == 0 or image_height == 0:
            return 1.0

        if self._fit_mode == "width":
            available_width = max(1, self._viewport_size.width() - FIT_WIDTH_SIDE_PADDING * 2)
            target_width = min(available_width, MAX_FIT_WIDTH_PAGE_WIDTH, image_width)
            return max(0.01, target_width / image_width)

        available_width = max(1, self._viewport_size.width() - VIEW_PADDING * 2)
        available_height = max(1, self._viewport_size.height() - VIEW_PADDING * 2)
        return min(available_width / image_width, available_height / image_height, 1.0)


def _pil_image_to_qimage(image: Image.Image) -> QImage:
    rgb = image.convert("RGB")
    data = rgb.tobytes("raw", "RGB")
    qimage = QImage(data, rgb.width, rgb.height, rgb.width * 3, QImage.Format.Format_RGB888)
    return qimage.copy()
