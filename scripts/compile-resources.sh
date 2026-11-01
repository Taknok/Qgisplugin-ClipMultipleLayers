#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/../ClipMultipleLayers"

temporary_output=$(mktemp)
trap 'rm -f "$temporary_output"' EXIT

pyside6-rcc -o "$temporary_output" resources.qrc

if ! grep -q '^from PySide6 import QtCore$' "$temporary_output"; then
    echo "Unexpected output from pyside6-rcc; resources.py was not updated." >&2
    exit 1
fi

sed 's/^from PySide6 import QtCore$/from qgis.PyQt import QtCore/' \
    "$temporary_output" > resources.py
