#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="${NIGHTLINE_VENV:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_DIR/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    echo "Nightline virtual environment was not found at: $VENV_DIR" >&2
    echo "Create it with: python3 -m venv \"$VENV_DIR\"" >&2
    echo "Then install dependencies with: \"$PYTHON\" -m pip install -r \"$PROJECT_ROOT/requirements.txt\"" >&2
    exit 1
fi

cd "$PROJECT_ROOT"

if ! "$PYTHON" -c "import nightline, PySide6" 2>/dev/null; then
    echo "Nightline dependencies are not installed in: $VENV_DIR" >&2
    echo "Run: \"$PYTHON\" -m pip install -r \"$PROJECT_ROOT/requirements.txt\"" >&2
    exit 1
fi

exec "$PYTHON" -m nightline.app "$@"
