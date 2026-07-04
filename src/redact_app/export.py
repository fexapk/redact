from __future__ import annotations

from io import BytesIO
import logging
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from redact_app.pdf_document import PdfDocument
from redact_app.redaction import RedactionRect


logger = logging.getLogger(__name__)

BLACK = (0, 0, 0)


def apply_redactions_to_image(
    image: Image.Image,
    rectangles: list[RedactionRect],
) -> Image.Image:
    """Return a copy of image with black redaction rectangles burned in."""
    redacted = image.copy()
    draw = ImageDraw.Draw(redacted)

    for rect in rectangles:
        clipped = rect.clipped(redacted.width, redacted.height)
        if clipped.is_empty:
            continue
        # Pillow rectangles include the endpoint, so subtract one pixel.
        draw.rectangle(
            [
                clipped.x,
                clipped.y,
                clipped.right - 1,
                clipped.bottom - 1,
            ],
            fill=BLACK,
        )

    return redacted


def export_redacted_pdf(
    source_path: Path,
    output_path: Path,
    redactions_by_page: dict[int, list[RedactionRect]],
    dpi: int = 200,
) -> None:
    """Export a new image-only PDF with redactions burned into raster pages."""
    source_path = Path(source_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting export source=%s output=%s dpi=%s",
        source_path,
        output_path,
        dpi,
    )

    with PdfDocument(source_path) as source_doc:
        output_doc = fitz.open()
        try:
            for page_index in range(source_doc.page_count):
                image = source_doc.render_page(page_index, dpi=dpi)
                rects = redactions_by_page.get(page_index, [])
                redacted_image = apply_redactions_to_image(image, rects)
                page_width, page_height = source_doc.page_size_points(page_index)

                page = output_doc.new_page(width=page_width, height=page_height)
                page.insert_image(
                    fitz.Rect(0, 0, page_width, page_height),
                    stream=_image_to_png_bytes(redacted_image),
                )
                logger.info(
                    "Exported page page=%s redactions=%s",
                    page_index,
                    len(rects),
                )

            output_doc.set_metadata({})
            output_doc.save(output_path, garbage=4, deflate=True)
        finally:
            output_doc.close()

    logger.info(
        "Exported redacted PDF path=%s pages=%s dpi=%s",
        output_path,
        page_index + 1 if "page_index" in locals() else 0,
        dpi,
    )


def _image_to_png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

