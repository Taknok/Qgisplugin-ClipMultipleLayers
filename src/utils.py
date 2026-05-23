# -*- coding: utf-8 -*-
"""
Utility functions for the Clip Multiple Layers plugin.
"""

import os

from qgis.core import QgsWkbTypes


def is_file_opened(file_path):
    """Check if a file is currently opened by trying to rename it."""
    if os.path.exists(file_path):
        try:
            os.rename(file_path, file_path + "_")
            os.rename(file_path + "_", file_path)
            return False
        except OSError:
            return True
    return False


def check_single_geom_type(layer):
    """
    Check if the layer has only single geometry types.
    Returns True if all features are single type, False otherwise.
    """
    for feature in layer.getFeatures():
        if not QgsWkbTypes.isSingleType(feature.geometry().wkbType()):
            return False
    return True


def get_unique_output_path(base_path, extension):
    """Generate a unique output path by appending version numbers if needed."""
    output = base_path + extension
    version = 0
    while is_file_opened(output):
        output = f"{base_path}({version}){extension}"
        version += 1
    return output
