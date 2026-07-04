from __future__ import annotations

import logging
from pathlib import Path

import fitz
from PIL import Image


logger = logging.getLogger(__name__)


class PdfDocument:
    """Read-only wrapper around a source PDF document."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._doc = fitz.open(self.path)
        logger.info("Opened PDF path=%s pages=%s", self.path, self.page_count)

    @property
    def page_count(self) -> int:
        return self._doc.page_count

    def page_size_points(self, page_index: int) -> tuple[float, float]:
        page = self._doc.load_page(page_index)
        return page.rect.width, page.rect.height

    def render_page(self, page_index: int, dpi: int) -> Image.Image:
        """Render a PDF page to an RGB Pillow image at the requested DPI."""
        page = self._doc.load_page(page_index)
        pixmap = page.get_pixmap(dpi=dpi, alpha=False)
        image = Image.frombytes(
            "RGB",
            (pixmap.width, pixmap.height),
            pixmap.samples,
        )
        logger.debug(
            "Rendered page page=%s dpi=%s width=%s height=%s",
            page_index,
            dpi,
            image.width,
            image.height,
        )
        return image

    def close(self) -> None:
        self._doc.close()
        logger.info("Closed PDF path=%s", self.path)

    def __enter__(self) -> "PdfDocument":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

