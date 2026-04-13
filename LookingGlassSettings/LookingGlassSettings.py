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


class LookingGlassSettings(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("Looking Glass settings")
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Holographic Display")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = [""]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#LookingGlassSettings">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
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
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        uiWidget = slicer.util.loadUI(self.resourcePath("UI/LookingGlassSettings.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        uiWidget.setMRMLScene(slicer.mrmlScene)
        self.setupConnections()


    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.disconnect()
        pass

    def enter(self) -> None:
        """Called each time the user opens this module."""
        pass

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        pass

    def setupConnections(self):
        """Setup signal/slot connections."""
        self.ui.focalPlaneSlider.valueChanged.connect(self.onFocalPlaneSliderChanged)

    def disconnect(self):
        """Disconnect signal/slot connections."""
        self.ui.focalPlaneSlider.valueChanged.disconnect(self.onFocalPlaneSliderChanged)

    def onFocalPlaneSliderChanged(self, value):
        """
        Modify focal plane depth of Looking Glass rendering.
        """
        try:
            # Get camera properties
            cameraNode = slicer.util.getNode('vtkMRMLCameraNode1')
            focalPoint = np.zeros(3)
            cameraNode.GetFocalPoint(focalPoint)
            pos = np.zeros(3)
            cameraNode.GetPosition(pos)

            # Calculate direction vector
            dx = focalPoint[0] - pos[0]
            dy = focalPoint[1] - pos[1]
            dz = focalPoint[2] - pos[2]
            distance = np.sqrt(dx * dx + dy * dy + dz * dz)

            # Calculate direction of projection (unit vector)
            directionOfProjection = np.zeros(3)
            directionOfProjection[0] = dx / distance
            directionOfProjection[1] = dy / distance
            directionOfProjection[2] = dz / distance

            # Convert slider value to desired focal plane distance
            minDistance = 500.0   # Minimum focal plane distance
            maxDistance = 2500.0   # Maximum focal plane distance
            newDistance = minDistance + (value / 100.0) * (maxDistance - minDistance)

            # Set focal point directly based on slider value
            focalPoint[0] = pos[0] + directionOfProjection[0] * newDistance
            focalPoint[1] = pos[1] + directionOfProjection[1] * newDistance
            focalPoint[2] = pos[2] + directionOfProjection[2] * newDistance

            # Set the new focal point back to the camera
            cameraNode.SetFocalPoint(focalPoint)
        except Exception as e:
            logging.warning(f'Camera node not available')

