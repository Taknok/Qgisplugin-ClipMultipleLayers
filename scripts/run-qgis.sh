#!/usr/bin/env bash
set -euo pipefail

exec env \
    -u PYTHONHOME \
    -u VIRTUAL_ENV \
    -u PYTHONUSERBASE \
    -u LD_LIBRARY_PATH \
    -u QT_PLUGIN_PATH \
    -u QT_QPA_PLATFORM_PLUGIN_PATH \
    PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
    PYTHONPATH="/usr/share/qgis/python:/usr/share/qgis/python/plugins" \
    QT_QPA_PLATFORM=wayland \
    /usr/bin/qgis "$@"
