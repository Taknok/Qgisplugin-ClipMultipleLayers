# -*- coding: utf-8 -*-
"""
Main plugin class for Clip Multiple Layers.
"""

import os
import tempfile
from qgis.core import Qgis, QgsProject, QgsVectorLayer, QgsRasterLayer
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.PyQt.QtGui import QIcon

from .clip_multiple_layers_dialog import ClipMultipleLayersDialog
from .clipper import LayerClipper


class ClipMultipleLayers:
    """Main plugin class."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        self.actions = []
        self.menu = self.tr("&Clip Multiple Layers")
        self.toolbar = self.iface.addToolBar("ClipMultipleLayers")
        self.toolbar.setObjectName("ClipMultipleLayers")
        self.dlg = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
        return message  # Placeholder for translation

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True,
                   add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar."""
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
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.add_action(
            icon_path,
            text=self.tr("Clip Multiple Layers"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Clip Multiple Layers"), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """Run method that performs all the real work."""
        if self.dlg is None:
            self.dlg = ClipMultipleLayersDialog()

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec()

        # See if OK was pressed
        if result:
            self._process_clipping()

    def _process_clipping(self):
        """Process the clipping operation."""
        # Get selected layers
        selected_layers = self.dlg.get_selected_layers()
        if not selected_layers:
            QMessageBox.warning(None, "No layers selected", "Please select at least one layer to clip.")
            return

        # Get mask layer
        mask_layer = self.dlg.get_mask_layer()
        if not mask_layer:
            QMessageBox.warning(None, "No mask selected", "Please select a mask layer.")
            return

        # Get output folder
        folder_name = self.dlg.get_output_folder()
        if not folder_name:
            QMessageBox.warning(None, "No output folder", "Please select an output folder.")
            return

        # Create output directories
        vector_dir = os.path.join(folder_name, "vectors")
        raster_dir = os.path.join(folder_name, "rasters")
        os.makedirs(vector_dir, exist_ok=True)
        os.makedirs(raster_dir, exist_ok=True)

        # Initialize clipper
        clipper = LayerClipper(self.iface, folder_name, self.dlg)

        # Exclude the mask layer from the selected layers to avoid clipping it
        try:
            mask_id = mask_layer.id()
            selected_layers = [layer for layer in selected_layers if layer.id() != mask_id]
        except Exception:
            # If anything goes wrong obtaining ids, fall back to original list
            pass

        # Process each layer
        for layer in selected_layers:
            if isinstance(layer, QgsVectorLayer):
                try:
                    clipper.clip_vector(layer, mask_layer)
                except Exception as e:
                    self.iface.messageBar().pushMessage(
                        "Error", f"Failed to clip vector layer {layer.name()}: {str(e)}",
                        level=Qgis.Critical
                    )
            elif isinstance(layer, QgsRasterLayer):
                try:
                    clipper.clip_raster(layer, mask_layer)
                except Exception as e:
                    self.iface.messageBar().pushMessage(
                        "Error", f"Failed to clip raster layer {layer.name()}: {str(e)}",
                        level=Qgis.Critical
                    )

        # Show error messages if any
        if clipper.multi_support_error:
            clipper.show_error_bar(clipper.multi_support_error)
        if clipper.multi_support_error_processing:
            clipper.show_error_bar(clipper.multi_support_error_processing)

        # Show success message
        self.iface.messageBar().pushMessage(
            "Success", f"Clipping completed. Output saved to {folder_name}",
            level=Qgis.Success
        )