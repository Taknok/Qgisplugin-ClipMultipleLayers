# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ClipMultipleLayers
                                 A QGIS plugin
 Clip all displayed layers (rasters and vectors) with a polygon layer selected.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-10-30
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Pg
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
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox, QProgressBar

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .clip_multiple_layers_dialog import ClipMultipleLayersDialog
import os.path
import errno

import processing, os, subprocess, time
from qgis.utils import *
from qgis.core import *
from qgis.gui import QgsMessageBar
# from qgis.PyQt.QtGui import QProgressBar
from qgis.PyQt.QtCore import *

from processing.algs.gdal.GdalUtils import GdalUtils

class ClipMultipleLayers:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ClipMultipleLayersDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Clip Multiple Layers')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ClipMultipleLayers')
        self.toolbar.setObjectName(u'ClipMultipleLayers')

        self.dlg.lineEdit.clear()
        self.initFolder();
        self.dlg.pushButton.clicked.connect(self.selectOutputFile);

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ClipMultipleLayers', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/clip_multiple_layers/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Clip all displayed layers'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Clip Multiple Layers'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def initFolder(self):
        path_project = QgsProject.instance().fileName()
        path_project = path_project[:path_project.rfind("/"):]

        self.folderName = path_project

        self.dlg.lineEdit.setText(self.folderName);

    def selectOutputFile(self):
        folderTmp = QFileDialog.getExistingDirectory(self.dlg,
            self.tr("Select output folder "), self.folderName)

        if folderTmp != "":
            self.folderName = folderTmp

        self.dlg.lineEdit.setText(self.folderName);

    def isFileOpened(self, file_path):
        if os.path.exists(file_path):
            try:
                os.rename(file_path, file_path+"_")
                os.rename(file_path+"_", file_path)
                return False
            except OSError as e:
                return True

    def run(self):
        """Run method that performs all the real work"""
        self.dlg.comboBox.clear()
        layers = QgsProject.instance().mapLayers().values()
        # fill selection combo, only polygon layers
        n = 0
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and \
                layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                self.dlg.comboBox.addItem( layer.name(), layer )
                n += 1

        if n == 0:  # no polygon layer
            iface.messageBar().pushMessage(self.tr("Warning"),
                self.tr("No polygon layer in actual project"),
                level=Qgis.Warning)
            return

        # show the dialog
        self.dlg.show()
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            dirName = self.dlg.lineEdit.text().strip()
            if len(dirName) == 0:
                iface.messageBar().pushMessage(self.tr("Warning"),
                    self.tr("Please select target folder"), level=Qgis.Warning)
                return
            if not (self.dlg.checkVector.isChecked() or
                    self.dlg.checkRaster.isChecked()):
                iface.messageBar().pushMessage(self.tr("Warning"),
                    self.tr("Neither vector nor raster layers selected for clipping. Nothing to do. "),
                    level=Qgis.Warning)
                return

            index = self.dlg.comboBox.currentIndex()
            selection = self.dlg.comboBox.itemData(index)
            
            checkedLayers = QgsProject.instance().layerTreeRoot().checkedLayers()
            
            #search existence of output folder, if not create it
            if not os.path.isdir(self.folderName):
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), self.folderName)

            directory = self.folderName + "/vectors"
            if not os.path.exists(directory) and self.dlg.checkVector.isChecked():
                os.makedirs(directory)
                
            directory = self.folderName + "/rasters"
            if not os.path.exists(directory) and self.dlg.checkRaster.isChecked():
                os.makedirs(directory)
            
            # Progress bar
            progressMessageBar = iface.messageBar().createMessage(self.tr("Clipping..."))
            progress = QProgressBar()
            progress.setMaximum(len(checkedLayers) - 1)
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
            progression = 0

            #clip part
            for layer in checkedLayers  :
                out = None
                # clip vector layer (if displayed and checked)
                if layer.type() == QgsMapLayer.VectorLayer and \
                   layer != selection and self.dlg.checkVector.isChecked():
                    output = self.folderName + "/vectors/clip_" + layer.name() + ".shp"
                    
                    # check file isn't openned and is writable
                    version = 0
                    while self.isFileOpened(output):
                        output = self.folderName + "/vectors/clip_" + \
                            layer.name() + "("+ str(version) + ").shp"
                        version +=1

                    processing.run("native:clip", {"INPUT" : layer.id(), "OVERLAY" : selection.id(), "OUTPUT" : output})

                    # save style
                    if self.dlg.checkStyle.isChecked():
                        qml_output = os.path.splitext(output)[0] + ".qml"
                        layer.saveNamedStyle(qml_output)
                        
                    # load layer
                    if self.dlg.checkBox.isChecked():
                        out = iface.addVectorLayer(output, "", "ogr")
                        if not out:
                            iface.messageBar().pushMessage(self.tr("Error"),
                                self.tr("Could not load ") +  output,
                                level=Qgis.Warning)
                
                # clip raster layer (if displayed and checked)
                if layer.type() == QgsMapLayer.RasterLayer and \
                   self.dlg.checkRaster.isChecked():
                    # get extension about the raster
                    filename, file_extension = os.path.splitext(layer.source())

                    output = self.folderName + "/rasters/clip_" + layer.name() + file_extension
                    
                    # check file isn't openned and is writable
                    version = 0
                    while self.isFileOpened(output):
                        output = self.folderName + "/rasters/clip_" + layer.name() + "("+ str(version) + ")" + file_extension
                        version +=1

                    processing.run("gdal:cliprasterbymasklayer", {"INPUT" : layer.id(), "MASK" : selection.id(), "CROP_TO_CUTLINE" : True,  "OUTPUT" : output})
                    
                    # load layer
                    if self.dlg.checkBox.isChecked():
                        out = iface.addRasterLayer(output, "")
                        if not out.isValid():
                            iface.messageBar().pushMessage(self.tr("Error"), self.tr("Could not load ") +  output, level=Qgis.Warning)
                
                # Update progression
                time.sleep(1)
                progress.setValue(progression + 1)
                progression += 1

            iface.messageBar().clearWidgets()