from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QToolBar,
)

from redact_app.export import export_redacted_pdf
from redact_app.page_view import PageView
from redact_app.pdf_document import PdfDocument
from redact_app.redaction import RedactionRect, RedactionStore


logger = logging.getLogger(__name__)

DEFAULT_DPI = 200


class MainWindow(QMainWindow):
    """Main application window for local raster PDF redaction."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Redact")
        self.resize(1000, 800)

        self._document: PdfDocument | None = None
        self._source_path: Path | None = None
        self._page_index = 0
        self._redactions = RedactionStore()
        self._selected_redaction: RedactionRect | None = None

        self._page_view = PageView()
        self._page_view.redaction_created.connect(self._add_redaction)
        self._page_view.selection_changed.connect(self._set_selected_redaction)
        self.setCentralWidget(self._page_view)

        self._build_toolbar()
        self._update_actions()
        self.statusBar().showMessage("Ready")

    def closeEvent(self, event: object) -> None:
        if self._document is not None:
            self._document.close()
        super().closeEvent(event)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self._open_action = QAction("Open PDF", self)
        self._open_action.triggered.connect(self._open_pdf)
        toolbar.addAction(self._open_action)

        self._previous_action = QAction("Previous", self)
        self._previous_action.triggered.connect(self._previous_page)
        toolbar.addAction(self._previous_action)

        self._page_action = QAction("Page 0 / 0", self)
        self._page_action.setEnabled(False)
        toolbar.addAction(self._page_action)

        self._next_action = QAction("Next", self)
        self._next_action.triggered.connect(self._next_page)
        toolbar.addAction(self._next_action)

        self._delete_action = QAction("Delete Box", self)
        self._delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self._delete_action.triggered.connect(self._delete_selected_redaction)
        toolbar.addAction(self._delete_action)
        self.addAction(self._delete_action)

        self._export_action = QAction("Export Redacted PDF", self)
        self._export_action.triggered.connect(self._export_pdf)
        toolbar.addAction(self._export_action)

    def _open_pdf(self) -> None:
        path_text, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF files (*.pdf)",
        )
        if not path_text:
            return

        path = Path(path_text)
        try:
            if self._document is not None:
                self._document.close()
            self._document = PdfDocument(path)
            self._source_path = path
            self._page_index = 0
            self._redactions.clear()
            self._selected_redaction = None
            self._render_current_page()
            self.statusBar().showMessage(f"Opened {path.name}")
        except Exception:
            logger.exception("Failed to open PDF path=%s", path)
            QMessageBox.critical(self, "Open Failed", "Could not open the selected PDF.")
        finally:
            self._update_actions()

    def _previous_page(self) -> None:
        if self._document is None or self._page_index == 0:
            return
        self._page_index -= 1
        self._render_current_page()
        self._update_actions()

    def _next_page(self) -> None:
        if self._document is None or self._page_index >= self._document.page_count - 1:
            return
        self._page_index += 1
        self._render_current_page()
        self._update_actions()

    def _add_redaction(self, rect: RedactionRect) -> None:
        self._redactions.add(rect)
        self._page_view.set_rectangles(self._redactions.for_page(self._page_index))
        self.statusBar().showMessage("Added redaction box")
        self._update_actions()

    def _set_selected_redaction(self, rect: object) -> None:
        self._selected_redaction = rect if isinstance(rect, RedactionRect) else None
        self._update_actions()

    def _delete_selected_redaction(self) -> None:
        if self._selected_redaction is None:
            return
        logger.info(
            "Deleted redaction page=%s x=%s y=%s width=%s height=%s",
            self._selected_redaction.page_index,
            self._selected_redaction.x,
            self._selected_redaction.y,
            self._selected_redaction.width,
            self._selected_redaction.height,
        )
        self._redactions.remove(self._selected_redaction)
        self._selected_redaction = None
        self._page_view.set_rectangles(self._redactions.for_page(self._page_index))
        self.statusBar().showMessage("Deleted redaction box")
        self._update_actions()

    def _export_pdf(self) -> None:
        if self._source_path is None:
            return

        default_path = self._source_path.with_name(
            f"{self._source_path.stem}-redacted.pdf"
        )
        path_text, _ = QFileDialog.getSaveFileName(
            self,
            "Export Redacted PDF",
            str(default_path),
            "PDF files (*.pdf)",
        )
        if not path_text:
            return

        output_path = Path(path_text)
        redactions_by_page = {
            page_index: self._redactions.for_page(page_index)
            for page_index in range(self._document.page_count if self._document else 0)
        }

        try:
            export_redacted_pdf(
                self._source_path,
                output_path,
                redactions_by_page,
                dpi=DEFAULT_DPI,
            )
            self.statusBar().showMessage(f"Exported {output_path.name}")
            QMessageBox.information(
                self,
                "Export Complete",
                "The redacted image-only PDF was exported.",
            )
        except Exception:
            logger.exception("Failed to export PDF path=%s", output_path)
            QMessageBox.critical(self, "Export Failed", "Could not export the PDF.")

    def _render_current_page(self) -> None:
        if self._document is None:
            return
        image = self._document.render_page(self._page_index, dpi=DEFAULT_DPI)
        self._page_view.set_page(
            self._page_index,
            image,
            self._redactions.for_page(self._page_index),
        )

    def _update_actions(self) -> None:
        has_document = self._document is not None
        page_count = self._document.page_count if self._document is not None else 0
        self._previous_action.setEnabled(has_document and self._page_index > 0)
        self._next_action.setEnabled(
            has_document and self._page_index < page_count - 1
        )
        self._delete_action.setEnabled(self._selected_redaction is not None)
        self._export_action.setEnabled(has_document)
        self._page_action.setText(
            f"Page {self._page_index + 1} / {page_count}"
            if has_document
            else "Page 0 / 0"
        )
