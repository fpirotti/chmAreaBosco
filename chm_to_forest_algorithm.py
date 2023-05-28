# -*- coding: utf-8 -*-

"""
/***************************************************************************
 CHMtoForest
                                 A QGIS plugin
 Converts a CHM to a vector layer with forest polygons according to various definitions
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-27
        copyright            : (C) 2023 by Francesco Pirotti - CIRGEO/TESAF University of Padova
        email                : francesco.pirotti@unipd.it
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

__author__ = 'Francesco Pirotti - CIRGEO/TESAF University of Padova'
__date__ = '2023-05-27'
__copyright__ = '(C) 2023 by Francesco Pirotti - CIRGEO/TESAF University of Padova'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import math
import shutil
import tempfile

from qgis import processing
from qgis.PyQt.QtGui import QIcon
from qgis.core import *
from qgis.utils import *
import inspect
import numpy as np
import sys
import os
dirname, filename = os.path.split(os.path.abspath(__file__))
import cv2 as cv
class CHMtoForestAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    tmpdir = ''
    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    PERC_COVER = 'PERC_COVER'
    MIN_AREA = 'MIN_AREA'
    MIN_LARGH = 'MIN_LARGH'
    ALTEZZA_MIN_ALBERO = 'ALTEZZA_MIN_ALBERO'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input CHM')
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ALTEZZA_MIN_ALBERO,
                self.tr('Soglia altezza albero'),
                defaultValue = 2.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PERC_COVER,
                self.tr('Copertura percentuale '),
                defaultValue = 20.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MIN_AREA,
                self.tr('Area minima'),
                defaultValue = 2000.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MIN_LARGH,
                self.tr('Larghezza minima'),
                defaultValue = 20.0
            )
        )

    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        return icon

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        if self.tmpdir == '':
            self.tmpdir = tempfile.TemporaryDirectory()
        else:
            self.tmpdir.cleanup()
            self.tmpdir = tempfile.TemporaryDirectory()

        chm_temppathfile_copy = os.path.join(self.tmpdir.name, '{}_copy.tif'.format( os.path.basename(source.source()).split('.')[0] ))

        shutil.copyfile(source.source(), chm_temppathfile_copy)
        rlayer = QgsRasterLayer(chm_temppathfile_copy, 'temp', 'gdal')
        provider = rlayer.dataProvider()

        feedback.setProgressText(source.source())
        feedback.setProgressText(chm_temppathfile_copy)

        temppathfile = self.parameterAsFileOutput(parameters, self.OUTPUT,  context)
        feedback.setProgressText(temppathfile)

        minarea = self.parameterAsDouble(parameters, self.MIN_AREA,  context)
        minlargh = self.parameterAsDouble(parameters, self.MIN_LARGH,  context)
        ksize = math.sqrt(minarea/3.14)
        minalt = self.parameterAsDouble(parameters, self.ALTEZZA_MIN_ALBERO,  context)
        # read the image
        img = cv.imread(source.source(), cv.IMREAD_ANYCOLOR | cv.IMREAD_ANYDEPTH  )

        block = QgsRasterBlock(Qgis.Byte, img.shape[0], img.shape[1])

        f = lambda x: int(x * 255)
        data = bytearray(np.array(map(f, img)))
        block.setData(data)
  
        provider.setEditable(True)
        provider.writeBlock(block, 1, 0, 0)
        provider.setEditable(False)


        if img is None:
            feedback.reportError( 'Cannot find or read ' + source.source() )
            return {}

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        feedback.setProgressText("Dimensione immagine: " + ' x '.join(map(str,img.shape)) )
        # binarize the image
        binr = cv.threshold(img, minalt, 255, cv.THRESH_BINARY  )[1]

        feedback.setProgressText("Applico soglia di altezza di : " + str(minalt) + ' metri ' )


        # Check for cancelation
        if feedback.isCanceled():
            return {}

        # define the kernel

        feedback.setProgressText("Creo un kernel di : " + str(round(ksize,3) ) +
                                 '(' + str(int(ksize)) +
                                 ') metri  e larghezza minima ' + str(minlargh) )
        kernel = np.ones((int(ksize), int(ksize)), np.uint8)

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        # invert the image
        invert = cv.bitwise_not(binr)

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        # erode the image
        erosion = cv.erode(invert, kernel,
                            iterations=1)

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        final = cv.dilate(erosion, kernel,
                            iterations=1)

        feedback.setProgressText("temppathfile")
        feedback.setProgressText(temppathfile)
        feedback.setProgressText("temppathfile")

        img = cv.imwrite(temppathfile, img)


        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: "sink"}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'CHM => Forest'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CHMtoForestAlgorithm()
