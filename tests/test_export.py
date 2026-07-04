from pathlib import Path

import fitz

from redact_app.export import export_redacted_pdf
from redact_app.redaction import RedactionRect


def test_export_creates_image_only_pdf_without_extractable_source_text(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source.pdf"
    output_path = tmp_path / "redacted.pdf"
    _create_text_pdf(source_path, "SECRET-12345")

    export_redacted_pdf(
        source_path=source_path,
        output_path=output_path,
        redactions_by_page={
            0: [RedactionRect(page_index=0, x=0, y=0, width=120, height=80)]
        },
        dpi=72,
    )

    with fitz.open(output_path) as doc:
        assert doc.page_count == 1
        assert "SECRET-12345" not in doc[0].get_text()
        assert len(doc[0].get_images()) == 1


def _create_text_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    try:
        page = doc.new_page(width=300, height=200)
        page.insert_text((40, 80), text, fontsize=18)
        doc.save(path)
    finally:
        doc.close()

