# Redact

Redact is a local desktop app for safely redacting sensitive information from
PDF files. It prioritizes redaction safety over preserving searchable text.

The app uses a conservative rasterization workflow:

1. Render each source PDF page to an image.
2. Draw user-selected black rectangles onto those page images.
3. Export a new PDF made only from the redacted images.

Because the exported PDF is image-based, source text, vector objects,
annotations, hidden layers, and other original PDF internals are discarded.

## Current Scope

- Open a local PDF.
- Navigate pages.
- Draw black redaction rectangles.
- Delete selected rectangles.
- Export a new image-only redacted PDF.
- Log major actions for auditability.

## Tradeoffs

- Output PDFs are not searchable.
- Text cannot be selected in exported PDFs.
- File size may be larger than the source PDF.
- Visual quality depends on the configured render DPI.

## Development

Install dependencies:

```powershell
python -m pip install -e ".[test]"
```

Run the app:

```powershell
python -m redact_app
```

Run tests:

```powershell
python -m pytest
```

## Safety Notes

Do not treat simple PDF overlay rectangles as secure redaction. This project
does not use overlay-only redaction. It exports a fresh rasterized PDF so the
covered source content is not present underneath the black boxes.

## License

Redact is licensed under `AGPL-3.0-or-later`.

This is the practical open-source choice for the current dependency set because
PyMuPDF is distributed under AGPL-3.0 or a commercial license. For this
non-commercial project, we use the AGPL path and keep the source open.
