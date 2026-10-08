#!/bin/bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
OUTPUT_DIR="$PROJECT_DIR/output"
ONEDRIVE_DIR="$HOME/OneDrive - moysies & partners GmbH/P-101-01 OZG BB/03_Projektarbeit/temp"
ENV_FILE="$PROJECT_DIR/.env"

if [[ -z "${AKDB_TOKEN:-}" && -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi

: "${AKDB_TOKEN:?Die Umgebungsvariable AKDB_TOKEN ist nicht gesetzt}"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Fehler: Python-Umgebung nicht gefunden: $PYTHON_BIN" >&2
    echo "Bitte im Projektverzeichnis ausführen: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

if [[ ! -d "$ONEDRIVE_DIR" ]]; then
    echo "Fehler: OneDrive-Zielverzeichnis nicht gefunden: $ONEDRIVE_DIR" >&2
    exit 1
fi

"$PYTHON_BIN" "$PROJECT_DIR/src/main.py"

echo "Feedback data export completed."
echo "Copying output files to OneDrive..."

shopt -s nullglob
output_files=("$OUTPUT_DIR"/outputFeedbacksAuslaenderwesen_*.xlsx)

if (( ${#output_files[@]} == 0 )); then
    echo "Fehler: Keine exportierten Feedback-Dateien in $OUTPUT_DIR gefunden." >&2
    exit 1
fi

cp "${output_files[@]}" "$ONEDRIVE_DIR/"

echo "Copied ${#output_files[@]} feedback files to: $ONEDRIVE_DIR"
