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

## Distribution and Installation

The project will provide a Linux installer that can be downloaded and executed
without first cloning the Git repository. The initial installer scope is
strictly Debian-based Linux distributions using `apt`; it must detect the
platform and package manager before making changes and abort with a clear
message on other operating systems or distributions.

The installer will:

1. Require a supported 64-bit Linux environment and a working shell.
2. Detect `apt-get` and the Debian package database. It must not attempt to
   guess or use another package manager.
3. Check for the system prerequisites `python3`, `python3-venv`, `python3-pip`,
   `curl`, `ca-certificates`, and `xdg-user-dirs`.
4. Use `sudo` to install missing prerequisites with `apt-get` when available.
   If privileges cannot be obtained, abort before downloading or installing
   the application. The installer must explain the packages it needs and must
   not silently run the entire application installer as root.
5. Download a versioned release archive and its published SHA-256 checksum.
   Git is not an installation prerequisite because the installer consumes the
   release archive rather than cloning the repository.
6. Verify the archive checksum before extracting or executing project code.
7. Install Redact and its Python dependencies into a user-local virtual
   environment, then create a user-local `redact` launcher.
8. Create a user application entry at
   `$XDG_DATA_HOME/applications/redact.desktop` (defaulting to
   `~/.local/share/applications`) so Redact appears in the desktop environment's
   application menu.
9. Resolve the user's desktop directory with `xdg-user-dir DESKTOP`. When that
   directory exists, copy the same entry there, mark it executable, and report
   the shortcut path. Do not assume the directory is named `Desktop`; if it
   cannot be resolved, keep the application-menu entry and continue.
10. Clean up temporary downloads and never modify source PDFs or a user's
   checkout.

Release archives must be published for each installable version, preferably as
GitHub Release assets. Each release must include:

- A source archive containing the application and packaging metadata.
- A matching `.sha256` checksum file.
- A stable version/tag identifier used by the installer.

The installer must use a pinned release version by default, support an explicit
version override for upgrades or rollbacks, and fail closed when the archive or
checksum is unavailable or does not match. A copy-and-paste command in the
README may download the installer script and execute it, but it must reference
an immutable version or release tag rather than an unpinned branch.

The first implementation supports only Linux. Windows PowerShell and
macOS/other Linux distributions continue to use the repository launchers until
separate installers are specified.

## MVP Features

- Open a local PDF.
- Navigate pages.
- View pages in fit-width mode by default, with fit-page available.
- Warn before export if not every page has been reviewed.
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
- Export review: pages are marked reviewed when opened; export warns if any
  pages remain unvisited and asks for final confirmation after all pages have
  been reviewed.

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
- Page review state uses human-readable page numbers for export warnings.

Manual verification should include:

- Open a PDF with visible text.
- Draw a black rectangle over text.
- Export.
- Confirm the exported PDF is visually redacted.
- Confirm text selection/extraction does not recover the source text.
