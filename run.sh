#!/bin/sh
# Run Redact from a local virtual environment.

set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV_DIR="$PROJECT_DIR/.venv"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    printf '%s\n' 'Python 3.11 or newer is required. Install Python, then run this script again.' >&2
    exit 1
fi

if ! "$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    printf '%s\n' 'Python 3.11 or newer is required. Install a supported Python version, then run this script again.' >&2
    exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
    printf '%s\n' 'Creating local virtual environment...'
    if ! "$PYTHON" -m venv "$VENV_DIR"; then
        printf '%s\n' "Could not create a virtual environment. Install your Python distribution's venv support, then run this script again." >&2
        exit 1
    fi
fi

if ! "$VENV_DIR/bin/python" -c 'import redact_app' >/dev/null 2>&1; then
    printf '%s\n' 'Installing Redact dependencies...'
    "$VENV_DIR/bin/python" -m pip install --disable-pip-version-check --editable "$PROJECT_DIR"
fi

exec "$VENV_DIR/bin/python" -m redact_app
