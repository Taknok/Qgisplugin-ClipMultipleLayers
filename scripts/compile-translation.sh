#!/bin/bash

for LOCALE in i18n/*.ts
do
    echo "Processing: ${LOCALE}.ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    pyside6-lrelease ${LOCALE} -qm "${LOCALE%.*}".qm
done

echo "✓ Translation compilation complete!"
echo "Remember to review and translate any 'unfinished' entries in the .ts files"
