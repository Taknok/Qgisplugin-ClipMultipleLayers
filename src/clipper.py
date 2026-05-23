# -*- coding: utf-8 -*-
"""
Clipping logic for the Clip Multiple Layers plugin.
"""

import os
import tempfile

from osgeo import gdal
from qgis import processing
from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsProject,
    QgsRasterFileWriter,
    QgsRasterLayer,
    QgsRasterPipe,
    QgsRasterProjector,
    QgsVectorFileWriter,
)
from qgis.PyQt.QtWidgets import QMessageBox

from .constants import FORMAT_NO_MULTI
from .utils import check_single_geom_type, get_unique_output_path


class LayerClipper:
    """Handles clipping operations for vector and raster layers."""

    def __init__(self, iface, folder_name, dlg):
        self.iface = iface
        self.folder_name = folder_name
        self.dlg = dlg
        self.multi_support_error = []
        self.multi_support_error_processing = []

    def clip_vector(self, layer, mask):
        """Clip a vector layer with the given mask."""
        index = self.dlg.comboBoxVectorFormat.currentIndex()
        vector_format = self.dlg.comboBoxVectorFormat.itemData(index)

        base_output = os.path.join(
            self.folder_name,
            "vectors",
            f"clip_{layer.name()}"
        )
        extension = vector_format.globs[0].lstrip("*")
        base_output = get_unique_output_path(base_output, extension)

        # Check for multi-geometry issues
        if (
            not check_single_geom_type(layer)
            and vector_format.driverName in FORMAT_NO_MULTI
        ):
            self.multi_support_error.append(layer)
            return

        result = processing.run(
            "native:clip",
            {"INPUT": layer.id(), "OVERLAY": mask.id(), "OUTPUT": "memory:"},
        )

        # Check processing result for multi-geometry
        if (
            not check_single_geom_type(result["OUTPUT"])
            and vector_format.driverName in FORMAT_NO_MULTI
        ):
            self.multi_support_error_processing.append(layer)
            return

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.fileEncoding = layer.dataProvider().encoding()
        options.driverName = vector_format.driverName
        options.fileEncoding = "UTF-8"

        write = QgsRasterFileWriter.writeAsVectorFormatV3

        error, error_msg, filename, _ = write(
            layer=result["OUTPUT"],
            fileName=base_output,
            transformContext=QgsProject.instance().transformContext(),
            options=options,
        )

        if error != QgsVectorFileWriter.NoError:
            self.iface.messageBar().pushMessage(
                "Error",
                f"Cannot write file {base_output}",
                level=Qgis.Critical
            )
            raise RuntimeError(error_msg)

        # Save style if checked
        if self.dlg.checkBoxSaveStyle.isChecked():
            qml_output = os.path.splitext(filename)[0] + ".qml"
            layer.saveNamedStyle(qml_output)

        # Load layer if checked
        if self.dlg.checkBoxLoadClippedLayers.isChecked():
            out = self.iface.addVectorLayer(filename, "", "ogr")
            if not out:
                self.iface.messageBar().pushMessage(
                    "Error", f"Could not load {filename}", level=Qgis.Warning
                )

    def _convert_to_gdal(self, layer, mask):
        """Convert non-GDAL layer to GDAL format for processing."""
        provider = layer.dataProvider()
        coord_transform_ctx = QgsProject.instance().transformContext()
        tr = QgsCoordinateTransform(
            mask.crs(),
            layer.crs(),
            QgsProject.instance()
        )

        pipe = QgsRasterPipe()
        projector = QgsRasterProjector()
        projector.setCrs(provider.crs(), provider.crs(), coord_transform_ctx)

        if not pipe.set(provider.clone()):
            self.iface.messageBar().pushMessage(
                "Error",
                f"Cannot set pipe provider: {layer.name()}",
                level=Qgis.Warning
            )
            return None, None

        if not pipe.insert(2, projector):
            self.iface.messageBar().pushMessage(
                "Error",
                f"Cannot set pipe projector: {layer.name()}",
                level=Qgis.Warning,
            )
            return None, None

        out_dir = tempfile.TemporaryDirectory()
        out_file = os.path.join(out_dir.name, "clipraster.tmp")
        file_writer = QgsRasterFileWriter(out_file)
        file_writer.Mode(0)

        extent = tr.transform(mask.extent())
        opts = ["COMPRESS=LZW"]
        file_writer.setCreateOptions(opts)

        error = file_writer.writeRaster(
            pipe,
            extent.width(),
            extent.height(),
            extent,
            layer.crs(),
            coord_transform_ctx,
        )

        if error == QgsRasterFileWriter.NoError:
            return QgsRasterLayer(out_file, layer.name()), out_dir
        else:
            self.iface.messageBar().pushMessage(
                "Error",
                f"Could not save temp raster: {layer.name()}",
                level=Qgis.Warning,
            )
            return None, None

    def _get_raster_extension(self, layer):
        """Get the appropriate extension for the raster layer."""
        dataset = gdal.Open(
            layer.dataProvider().dataSourceUri(),
            gdal.GA_ReadOnly
        )
        driver_name = dataset.GetDriver().ShortName
        return QgsRasterFileWriter.extensionsForFormat(driver_name)[0]

    def clip_raster(self, layer, mask):
        """Clip a raster layer with the given mask."""
        tmp_dir = None
        if layer.providerType() != "gdal":
            layer, tmp_dir = self._convert_to_gdal(layer, mask)
            if layer is None:
                return

        filename = layer.name()
        file_extension = self._get_raster_extension(layer)
        base_output = os.path.join(
            self.folder_name,
            "rasters",
            f"clip_{filename}"
        )
        output = get_unique_output_path(base_output, f".{file_extension}")

        processing.run(
            "gdal:cliprasterbymasklayer",
            {
                "INPUT": layer,
                "MASK": mask,
                "CROP_TO_CUTLINE": True,
                "OUTPUT": output
            },
        )

        if tmp_dir is not None:
            del layer
            tmp_dir.cleanup()

        if self.dlg.checkBoxLoadClippedLayers.isChecked():
            out = self.iface.addRasterLayer(output, "")
            if out is None or not out.isValid():
                self.iface.messageBar().pushMessage(
                    "Error", f"Could not load {output}", level=Qgis.Warning
                )

    def show_error_popup(self, error_arr):
        """Show a popup with error details."""
        text = (
            f"{' & '.join(error_arr)} do not support multitype geometry. "
            f"Please change output format or convert to singletype geometry.\n"
            f"{[layer.name() for layer in self.multi_support_error]}"
        )
        QMessageBox.warning(None, "Multi Type format error", text)

    def show_error_bar(self, error_arr):
        """Show an error message in the message bar."""
        from qgis.PyQt.QtWidgets import QPushButton

        widget = self.iface.messageBar().createMessage(
            "Skipped Layers", "Some layers were not processed"
        )
        button = QPushButton(widget)
        button.setText("More")
        button.clicked.connect(lambda: self.show_error_popup(error_arr))
        widget.layout().addWidget(button)
        self.iface.messageBar().pushWidget(widget, Qgis.Warning)
