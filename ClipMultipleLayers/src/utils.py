# -*- coding: utf-8 -*-
"""
Utility functions for the Clip Multiple Layers plugin.
"""

import os

from qgis.core import QgsWkbTypes


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
    while os.path.exists(output):
        output = f"{base_path}({version}){extension}"
        version += 1
    return output
