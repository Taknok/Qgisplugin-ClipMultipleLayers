# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ClipMultipleLayersDialog
                                 A QGIS plugin
 Clip all display layers (rasters and vectors) with a layer named selection for model
                             -------------------
        begin                : 2015-05-18
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Pg
        email                : pg.developper.fr@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Clip_Multiple_Layers_dialog_base.ui'))


class ClipMultipleLayersDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ClipMultipleLayersDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
