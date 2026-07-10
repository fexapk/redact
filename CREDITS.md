# Credits

Redact started as a collaboration between Fex and Ava.

## Fex

- Project owner.
- Defined the product goal: a simple local app for redacting sensitive PDF
  information with black rectangles.
- Chose the safety-first rasterization approach over overlay-only PDF
  redaction.
- Set the project values: minimal, efficient, local, human-readable,
  documented, commented, and auditable.
- Reviewed and approved the implementation direction.

## Ava

- AI coding agent and implementation collaborator.
- Designed the initial Python, PySide6, PyMuPDF, and Pillow architecture.
- Implemented the first working raster redaction MVP.
- Added the Git history, implementation spec, tests, README, license metadata,
  and future-agent guidance.
- Preserved the core safety invariant: exported PDFs are rebuilt from redacted
  page images rather than original PDF content with overlay rectangles.

## Lin

- AI coding agent and implementation collaborator.
- Added the cross-platform launchers and clone-and-run installation guidance.
