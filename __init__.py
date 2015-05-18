# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ClipMultipleLayers
                                 A QGIS plugin
 Clip all display layers (rasters and vectors) with a layer named selection for model
                             -------------------
        begin                : 2015-05-18
        copyright            : (C) 2015 by Pg
        email                : pg.developper.fr@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ClipMultipleLayers class from file ClipMultipleLayers.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Clip_Multiple_Layers import ClipMultipleLayers
    return ClipMultipleLayers(iface)
