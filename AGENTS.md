# Redact Agent Guide

## Project Identity

Redact is a small local desktop app for safely redacting PDFs. It is built for
Fex as a minimal, understandable tool rather than a platform or service.

The app's defining choice is safety through rasterization:

1. Render each PDF page to an image.
2. Burn black redaction rectangles into the image pixels.
3. Export a new image-only PDF.

Do not replace this with overlay-only PDF rectangles. Overlay rectangles can
leave the original text, images, vectors, annotations, or hidden layers
recoverable underneath.

## Engineering Philosophy

- Keep the app local-first and offline-friendly.
- Prefer small, deterministic modules over clever abstractions.
- Keep code human-readable for future agents and human maintainers.
- Preserve auditability with clear logging around file opens, redaction edits,
  and exports.
- Do not log document text contents or sensitive extracted data.
- Preserve original PDFs; export new files instead of mutating inputs.
- Treat dependencies and licensing as design constraints, not afterthoughts.
- Favor explicit behavior and clear errors over hidden automation.

## Current Stack

- Python
- PySide6 for the desktop UI
- PyMuPDF for PDF loading, rendering, and PDF output
- Pillow for image drawing
- pytest for focused tests

PyMuPDF is AGPL-3.0-or-commercial. This project is non-commercial and should
remain open source under AGPL-3.0-or-later unless the PDF engine changes.

## Safety Invariants

- Export must render pages fresh from the source PDF.
- Exported PDFs must contain redacted page images, not original page objects
  with black boxes over them.
- Redaction rectangles are stored in rendered-image pixel coordinates.
- The source PDF must never be modified in place.
- Tests should continue checking that exported sample PDFs do not expose source
  text via extraction.

## Useful Commands

Run the app after cloning:

```powershell
.\run.ps1
```

```sh
sh ./run.sh
```

Install for development:

```powershell
python -m pip install -e ".[test]"
```

Run tests:

```powershell
python -m pytest
```

Run the app:

```powershell
python -m redact_app
```

## Before Changing Behavior

Read:

- `docs/implementation-spec.md`
- `src/redact_app/export.py`
- `src/redact_app/redaction.py`
- `tests/test_export.py`

If a change weakens the rasterization safety model, document the reason clearly
and add verification that sensitive source content is not recoverable.
