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
- View pages in fit-width mode by default, with fit-page available.
- Warn before export if not every page has been reviewed.
- Draw black redaction rectangles.
- Delete selected rectangles.
- Export a new image-only redacted PDF.
- Log major actions for auditability.

## Tradeoffs

- Output PDFs are not searchable.
- Text cannot be selected in exported PDFs.
- File size may be larger than the source PDF.
- Visual quality depends on the configured render DPI.

## Install and Run

Redact requires Python 3.11 or newer. Clone this repository, then run the
launcher for your operating system from the repository directory. On its first
run, it creates a local `.venv` virtual environment, installs Redact and its
runtime dependencies there, and opens the app. Later runs reuse that environment.

### Debian-based Linux (one command)

```sh
curl -fsSL https://raw.githubusercontent.com/fexapk/redact/v0.1.0/install.sh | bash
```

Review the versioned script URL before running it if you prefer not to pipe
remote content directly to a shell.

The installer supports 64-bit Debian-based Linux only. It uses `apt` and
`sudo` to install missing system prerequisites, downloads the pinned release
archive, verifies its checksum, and installs Redact under
`~/.local/share/redact` with a launcher in `~/.local/bin`. It does not require
Git. To install another published version, set `REDACT_VERSION`, for example
`REDACT_VERSION=v0.1.0 bash -c "$(curl -fsSL https://raw.githubusercontent.com/fexapk/redact/v0.1.0/install.sh)"`.

### Windows PowerShell

```powershell
.\run.ps1
```

If PowerShell blocks local scripts, run it once for this session and try again:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

### Linux and macOS

```sh
sh ./run.sh
```

## Development

For the test tools, install the project with its `test` extra in your active
Python environment:

```sh
python -m pip install -e ".[test]"
python -m pytest
```

## Viewer Behavior

The viewer defaults to `Fit Width` so dense PDFs are readable on a 1920x1080
monitor. The page is capped at a comfortable maximum display width and centered
with side padding, so it does not consume the whole screen on wide displays.

Use `Fit Page` when you want to see the entire page at once.

## Export Review Prompts

Each page is marked reviewed when it is opened in the viewer. If you try to
export before visiting every page, Redact warns you and lists the unreviewed
pages. If every page has been visited, Redact still asks for one final
confirmation before writing the redacted PDF.

## Safety Notes

Do not treat simple PDF overlay rectangles as secure redaction. This project
does not use overlay-only redaction. It exports a fresh rasterized PDF so the
covered source content is not present underneath the black boxes.

## License

Redact is licensed under `AGPL-3.0-or-later`.

This is the practical open-source choice for the current dependency set because
PyMuPDF is distributed under AGPL-3.0 or a commercial license. For this
non-commercial project, we use the AGPL path and keep the source open.

## Credits

See `CREDITS.md` for project contribution credits.
