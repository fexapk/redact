# Implementation Spec

## Goal

Build a minimal local desktop app that lets a user redact sensitive PDF content
by drawing black rectangles. The app prioritizes maximum redaction safety over
preserving searchable or selectable text.

## Security Model

The app never saves overlay-only PDF rectangles. Overlay-only redaction can
leave text or images recoverable underneath the black box.

Instead, export uses this raster workflow:

1. Render every source PDF page to an RGB image at a fixed DPI.
2. Burn user redaction rectangles into those images.
3. Create a new PDF containing only the redacted page images.

The exported PDF should contain no original text layer, vector objects,
annotations, metadata, or hidden PDF structure from the source.

## Stack

- Python for implementation.
- PySide6 for the local desktop GUI.
- PyMuPDF for PDF loading, rendering, and output PDF creation.
- Pillow for image drawing.
- Python `logging` for audit-friendly local logs.
- pytest for focused tests.

## MVP Features

- Open a local PDF.
- Navigate pages.
- View pages in fit-width mode by default, with fit-page available.
- Draw redaction boxes with the mouse.
- Select and delete a redaction box.
- Export a new image-only redacted PDF.
- Log major actions without logging document text contents.

## Non-Goals

- OCR.
- Text search.
- Automatic sensitive-data detection.
- Preserving selectable text.
- Preserving source annotations, forms, layers, or signatures.
- Cloud upload or remote processing.

## Coordinate Model

Redaction rectangles are stored in rendered page-image pixel coordinates:

```python
RedactionRect(page_index=0, x=100, y=120, width=300, height=40)
```

The current MVP uses the same DPI for preview and export, so preview
coordinates map directly to the exported raster image.

## Default Settings

- DPI: 200.
- Image mode: RGB.
- Redaction color: black.
- Output: one image per PDF page.
- Viewer: fit-width by default, with side padding and a maximum page display
  width so dense documents stay readable without filling wide monitors.

## Audit Logging

The app logs:

- App start and log path.
- Source PDF path and page count.
- Redaction rectangle creation and deletion.
- Export path, page count, DPI, and per-page redaction counts.
- Exceptions with stack traces.

The app does not log document text contents.

## Verification

Automated tests cover:

- Rectangle normalization and clipping.
- Pixel-level black-box drawing.
- Exported PDF page count.
- Exported PDF text extraction does not include source text.

Manual verification should include:

- Open a PDF with visible text.
- Draw a black rectangle over text.
- Export.
- Confirm the exported PDF is visually redacted.
- Confirm text selection/extraction does not recover the source text.
