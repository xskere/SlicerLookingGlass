import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import numpy as np
import logging

#
# LookingGlassSettings
#

# Predefined quilt configurations per device type.
# Mirrors GetSettingsByDevice() in vtkLookingGlassInterface.cxx.
DEVICE_CONFIGS = {
    "standard":   {"name": 'Looking Glass 8.9"',                          "tilesX":  4, "tilesY": 8, "quiltW": 2048, "quiltH": 2048},
    "portrait":   {"name": "Looking Glass Portrait",                       "tilesX":  8, "tilesY": 6, "quiltW": 3360, "quiltH": 3360},
    "large":      {"name": 'Looking Glass 16"',                            "tilesX":  5, "tilesY": 9, "quiltW": 4096, "quiltH": 4096},
    "8k":         {"name": 'Looking Glass 32"',                            "tilesX":  5, "tilesY": 9, "quiltW": 8192, "quiltH": 8192},
    "8k_gen2":    {"name": 'Looking Glass 32" (gen2)',                     "tilesX":  5, "tilesY": 9, "quiltW": 8192, "quiltH": 8192},
    "65":         {"name": 'Looking Glass 65"',                            "tilesX":  8, "tilesY": 9, "quiltW": 8192, "quiltH": 8192},
    "go_p":       {"name": "Looking Glass Go Portrait",                    "tilesX": 11, "tilesY": 6, "quiltW": 4092, "quiltH": 4092},
    "4k_gen2":    {"name": 'Looking Glass 16" (4K gen2)',                  "tilesX":  5, "tilesY": 9, "quiltW": 4095, "quiltH": 4095},
    "65_gen2":    {"name": 'Looking Glass 65" (gen2)',                     "tilesX":  8, "tilesY": 9, "quiltW": 8192, "quiltH": 8192},
    "16_gen3_l":  {"name": 'Looking Glass 16" Light Field (Landscape)',    "tilesX":  7, "tilesY": 7, "quiltW": 5999, "quiltH": 5999},
    "16_gen3_p":  {"name": 'Looking Glass 16" Light Field (Portrait)',     "tilesX": 11, "tilesY": 6, "quiltW": 5995, "quiltH": 6000},
    "27_gen3_l":  {"name": 'Looking Glass 27" Light Field (Landscape)',    "tilesX":  8, "tilesY": 6, "quiltW": 7680, "quiltH": 4320},
    "27_gen3_p":  {"name": 'Looking Glass 27" Light Field (Portrait)',     "tilesX": 12, "tilesY": 4, "quiltW": 7680, "quiltH": 4320},
    "32_gen3_l":  {"name": 'Looking Glass 32" Light Field (Landscape)',    "tilesX":  7, "tilesY": 7, "quiltW": 8190, "quiltH": 8190},
    "32_gen3_p":  {"name": 'Looking Glass 32" Light Field (Portrait)',     "tilesX": 12, "tilesY": 4, "quiltW": 8184, "quiltH": 8184},
}


class LookingGlassSettings(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("Looking Glass settings")
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Holographic Display")]
        self.parent.dependencies = []
        self.parent.contributors = [""]
        self.parent.helpText = _("""
Fine-tune Looking Glass display settings including quilt tile layout and focal plane.
""")
        self.parent.acknowledgementText = _("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")

#
# LookingGlassSettingsWidget
#


class LookingGlassSettingsWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None
        self._updatingSpinBoxes = False

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        uiWidget = slicer.util.loadUI(self.resourcePath("UI/LookingGlassSettings.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        uiWidget.setMRMLScene(slicer.mrmlScene)

        self._populateDeviceTypeComboBox()
        self.setupConnections()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.disconnect()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        pass

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        pass

    # ---------------------------------------------------------------------------
    # Helpers

    def _populateDeviceTypeComboBox(self):
        """Fill the device type combo box with all known device configurations."""
        cb = self.ui.deviceTypeComboBox
        cb.blockSignals(True)
        cb.clear()
        for deviceType, cfg in DEVICE_CONFIGS.items():
            cb.addItem(cfg["name"], deviceType)
        # Default to "large" as it is the default in vtkLookingGlassInterface
        defaultIndex = cb.findData("large")
        if defaultIndex >= 0:
            cb.setCurrentIndex(defaultIndex)
            self._updateSpinBoxesFromConfig("large")
        cb.blockSignals(False)

    def _updateSpinBoxesFromConfig(self, deviceType):
        """Update tile/quilt size spinboxes from a known device config dict."""
        cfg = DEVICE_CONFIGS.get(deviceType)
        if cfg is None:
            return
        self._updatingSpinBoxes = True
        self.ui.quiltTilesXSpinBox.setValue(cfg["tilesX"])
        self.ui.quiltTilesYSpinBox.setValue(cfg["tilesY"])
        self.ui.quiltWidthSpinBox.setValue(cfg["quiltW"])
        self.ui.quiltHeightSpinBox.setValue(cfg["quiltH"])
        self._updatingSpinBoxes = False

    def _getLookingGlassViewNode(self):
        """Return the vtkMRMLLookingGlassViewNode, or None if not available."""
        try:
            lgLogic = slicer.modules.lookingglass.logic()
            return lgLogic.GetLookingGlassViewNode()
        except Exception:
            return None

    # ---------------------------------------------------------------------------
    # Connections

    def setupConnections(self):
        """Setup signal/slot connections."""
        self.ui.deviceTypeComboBox.currentIndexChanged.connect(self.onDeviceTypeComboBoxChanged)
        self.ui.applyCustomQuiltButton.clicked.connect(self.onApplyCustomQuiltButtonClicked)
        self.ui.focalPlaneSlider.valueChanged.connect(self.onFocalPlaneSliderChanged)

    def disconnect(self):
        """Disconnect signal/slot connections."""
        self.ui.deviceTypeComboBox.currentIndexChanged.disconnect(self.onDeviceTypeComboBoxChanged)
        self.ui.applyCustomQuiltButton.clicked.disconnect(self.onApplyCustomQuiltButtonClicked)
        self.ui.focalPlaneSlider.valueChanged.disconnect(self.onFocalPlaneSliderChanged)

    # ---------------------------------------------------------------------------
    # Slots

    def onDeviceTypeComboBoxChanged(self, index):
        """Apply a predefined quilt configuration by device type."""
        deviceType = self.ui.deviceTypeComboBox.itemData(index)
        if not deviceType:
            return

        # Update spinboxes to reflect the chosen preset
        self._updateSpinBoxesFromConfig(deviceType)

        lgViewNode = self._getLookingGlassViewNode()
        if lgViewNode is None:
            logging.warning("LookingGlassSettings: view node not available — settings will be applied when the device connects.")
            return

        # Clear custom tile values so device-type preset is used
        lgViewNode.SetQuiltTilesX(0)
        lgViewNode.SetQuiltTilesY(0)
        lgViewNode.SetQuiltWidth(0)
        lgViewNode.SetQuiltHeight(0)
        lgViewNode.SetDeviceType(deviceType)

    def onApplyCustomQuiltButtonClicked(self):
        """Apply custom quilt tile and size values from the spinboxes."""
        lgViewNode = self._getLookingGlassViewNode()
        if lgViewNode is None:
            logging.warning("LookingGlassSettings: view node not available — connect the Looking Glass device first.")
            return

        lgViewNode.SetDeviceType("")
        lgViewNode.SetQuiltTilesX(self.ui.quiltTilesXSpinBox.value)
        lgViewNode.SetQuiltTilesY(self.ui.quiltTilesYSpinBox.value)
        lgViewNode.SetQuiltWidth(self.ui.quiltWidthSpinBox.value)
        lgViewNode.SetQuiltHeight(self.ui.quiltHeightSpinBox.value)

    def onFocalPlaneSliderChanged(self, value):
        """Modify focal plane depth of Looking Glass rendering."""
        try:
            cameraNode = slicer.util.getNode('vtkMRMLCameraNode1')
            focalPoint = np.zeros(3)
            cameraNode.GetFocalPoint(focalPoint)
            pos = np.zeros(3)
            cameraNode.GetPosition(pos)

            dx = focalPoint[0] - pos[0]
            dy = focalPoint[1] - pos[1]
            dz = focalPoint[2] - pos[2]
            distance = np.sqrt(dx * dx + dy * dy + dz * dz)

            directionOfProjection = np.array([dx, dy, dz]) / distance

            minDistance = 500.0
            maxDistance = 2500.0
            newDistance = minDistance + (value / 100.0) * (maxDistance - minDistance)

            focalPoint[:] = pos + directionOfProjection * newDistance
            cameraNode.SetFocalPoint(focalPoint)
        except Exception:
            logging.warning("LookingGlassSettings: camera node not available")
