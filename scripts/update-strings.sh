#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob
translation_files=(i18n/*.ts)

if ((${#translation_files[@]} == 0)); then
    echo "No translation files found in i18n/." >&2
    exit 1
fi

for translation_file in "${translation_files[@]}"; do
    echo "Updating ${translation_file}"
    pylupdate6 --no-obsolete src/ui/*.ui -ts "$translation_file"
done
