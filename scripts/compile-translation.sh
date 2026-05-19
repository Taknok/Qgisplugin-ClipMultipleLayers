#!/bin/bash
LRELEASE=$1
LOCALES=$2

set -e

for LOCALE in ${LOCALES}
do
    echo "Processing: ${LOCALE}.ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    pyside6-lrelease i18n/${LOCALE}.ts -qm i18n/${LOCALE}.qm
done

echo "✓ Translation compilation complete!"
echo "Remember to review and translate any 'unfinished' entries in the .ts files"
