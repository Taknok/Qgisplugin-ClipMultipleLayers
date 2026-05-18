# -*- coding: utf-8 -*-
"""
Dialog for the Clip Multiple Layers plugin.
"""

import os

from qgis.PyQt import QtCore, QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsWkbTypes, QgsVectorFileWriter

from .clip_multiple_layers_dialog_ui import Ui_ClipMultipleLayers


class ClipMultipleLayersDialog(QtWidgets.QDialog, Ui_ClipMultipleLayers):
    """Dialog for selecting clipping parameters."""

    def __init__(self, parent=None):
        """Constructor."""
        super(ClipMultipleLayersDialog, self).__init__(parent)
        self.setupUi(self)
        self.folder_name = ""

        # Initialize folder
        self.init_folder()
        self.pushButtonOutputFolder.clicked.connect(self.select_output_folder)

        # Populate dialog
        self.populate_dialog()

    def init_folder(self):
        """Initialize the output folder with the project directory."""
        path_project = QgsProject.instance().fileName()
        self.folder_name = os.path.dirname(path_project)
        self.lineEditOutputFolder.setText(self.folder_name)

    def select_output_folder(self):
        """Open a dialog to select the output folder."""
        from qgis.PyQt.QtWidgets import QFileDialog
        folder_tmp = QFileDialog.getExistingDirectory(
            self, "Select output folder", self.folder_name
        )
        if folder_tmp:
            self.folder_name = folder_tmp
            self.lineEditOutputFolder.setText(self.folder_name)

    def populate_dialog(self):
        """Populate the dialog with available layers and formats."""
        self._populate_layer_selection()

        # Clear and populate mask layer combo box
        self.comboBoxMaskLayer.clear()
        layers = QgsProject.instance().mapLayers().values()

        polygon_count = 0
        for layer in layers:
            if (layer.type() == QgsMapLayer.VectorLayer and
                layer.geometryType() == QgsWkbTypes.PolygonGeometry):
                self.comboBoxMaskLayer.addItem(layer.name(), layer)
                polygon_count += 1

        # Populate vector format combo box
        for vector_format in QgsVectorFileWriter.supportedFiltersAndFormats():
            self.comboBoxVectorFormat.addItem(vector_format.driverName, vector_format)

        if polygon_count == 0:
            from qgis.utils import iface
            iface.messageBar().pushMessage(
                "Warning", "No polygon layer in current project", level=Qgis.Warning
            )

    def _populate_layer_selection(self):
        """Populate the layer selection table with project layers."""
        self.tableWidgetLayerSelection.clearContents()
        self.tableWidgetLayerSelection.setRowCount(0)
        self.tableWidgetLayerSelection.setColumnCount(2)
        self.tableWidgetLayerSelection.setHorizontalHeaderLabels(["", "Layer"])
        self.tableWidgetLayerSelection.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetLayerSelection.verticalHeader().setVisible(False)
        try:
            selection_behavior = QtWidgets.QAbstractItemView.SelectRows
        except AttributeError:
            selection_behavior = QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        self.tableWidgetLayerSelection.setSelectionBehavior(selection_behavior)

        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            row = self.tableWidgetLayerSelection.rowCount()
            self.tableWidgetLayerSelection.insertRow(row)

            visible = False
            layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
            if layer_tree_layer is not None:
                visible = layer_tree_layer.isVisible()

            checkbox_item = QtWidgets.QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked)
            checkbox_item.setText("")
            self.tableWidgetLayerSelection.setItem(row, 0, checkbox_item)

            layer_item = QtWidgets.QTableWidgetItem(layer.name())
            layer_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            layer_item.setData(Qt.ItemDataRole.UserRole, layer.id())
            self.tableWidgetLayerSelection.setItem(row, 1, layer_item)

        self.tableWidgetLayerSelection.resizeColumnsToContents()

    def get_selected_layers(self):
        """Get the selected layers to clip from the layer selection table."""
        selected_layers = []
        for row in range(self.tableWidgetLayerSelection.rowCount()):
            checkbox_item = self.tableWidgetLayerSelection.item(row, 0)
            if checkbox_item is None or checkbox_item.checkState() != Qt.CheckState.Checked:
                continue

            layer_item = self.tableWidgetLayerSelection.item(row, 1)
            if layer_item is None:
                continue

            layer_id = layer_item.data(Qt.ItemDataRole.UserRole)
            if layer_id is None:
                continue
            # Ensure we pass a native string id to mapLayer
            try:
                layer_id = str(layer_id)
            except Exception:
                continue

            layer = QgsProject.instance().mapLayer(layer_id)
            if layer is None:
                continue

            if layer.type() == QgsMapLayer.VectorLayer and self.checkVector.isChecked():
                selected_layers.append(layer)
            elif layer.type() == QgsMapLayer.RasterLayer and self.checkRaster.isChecked():
                selected_layers.append(layer)

        return selected_layers

    def get_mask_layer(self):
        """Get the selected mask layer."""
        index = self.comboBoxMaskLayer.currentIndex()
        if index >= 0:
            return self.comboBoxMaskLayer.itemData(index)
        return None

    def get_output_folder(self):
        """Get the output folder path."""
        return self.lineEditOutputFolder.text().strip()