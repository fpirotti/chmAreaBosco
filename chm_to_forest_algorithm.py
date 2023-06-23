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

import numpy as np
#import tempfile
from qgis.PyQt.Qt import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.utils import *
import inspect
import sys
import os
#from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFileDestination)

dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname)
import cv2 as cv
from osgeo import gdal
import processing
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
    INPUT_SIBOSCO = 'INPUT_SIBOSCO'
    INPUT_NOBOSCO = 'INPUT_NOBOSCO'
    # PERC_COVER = 'PERC_COVER'
    # MIN_AREA = 'MIN_AREA'
    # MIN_LARGH = 'MIN_LARGH'
    # ALTEZZA_MIN_ALBERO = 'ALTEZZA_MIN_ALBERO'

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

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_SIBOSCO,
                self.tr('Input Maschera Pixel Bosco'),
                optional=True, defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_NOBOSCO,
                self.tr('Input Maschera Pixel No-Bosco'),
                optional=True, defaultValue=None
            )
        )
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Output layer OPEN')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink('keypoints', 'Keypoints',
                                                  type=QgsProcessing.TypeVectorPoint,
                                              createByDefault=True, defaultValue=None))

        self.addParameter(
            QgsProcessingParameterNumber(
                'altezza_alberochioma_m',
                self.tr('Soglia altezza chioma (m)'),
                defaultValue=2.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                'densit_minima_percentuale',
                self.tr('Densità copertura (%)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=20.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'area_minima_m2',
                self.tr('Area minima (m2)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=2000.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                'larghezza_minima_m',
                self.tr('Larghezza minima'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=20.0
            )
        )

    #def icon(self):
        #cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        #icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        #return icon

    def local2src(self, x, y, dataProvider, verbose=False ):
        x1 = 0
        y1 = 0
        if isinstance(dataProvider, QgsRasterDataProvider):
            ext = QgsRectangle(dataProvider.extent())
            x1 = ext.xMinimum() + (x * ((ext.xMaximum()-ext.xMinimum())/dataProvider.xSize()))
            y1 = ext.yMaximum() - (y * ((ext.yMaximum()-ext.yMinimum())/dataProvider.ySize()))
            if verbose:
                print( str(x) + ' - ' + str(x1)   )

        return x1, y1

    def _create_points(self, kp1, sdp):
        """Create points for testing"""

        point_layer = QgsVectorLayer('Point?crs=EPSG:4326', 'keypoints', 'memory')

        point_provider = point_layer.dataProvider()
        point_provider.addAttributes([QgsField('X', QVariant.Double)])
        point_provider.addAttributes([QgsField('Y', QVariant.Double)])
        #x_index = point_provider.fieldNameIndex('X')
        #y_index = point_provider.fieldNameIndex('Y')
        point_provider.addAttributes([QgsField('sizeX', QVariant.Double)])
        point_provider.addAttributes([QgsField('angle', QVariant.Double)])
        point_provider.addAttributes([QgsField('response', QVariant.Double)])
        point_provider.addAttributes([QgsField('octave', QVariant.Int)])
        #s_index = point_provider.fieldNameIndex('size')
        #a_index = point_provider.fieldNameIndex('angle')
        #r_index = point_provider.fieldNameIndex('response')
        #o_index = point_provider.fieldNameIndex('octave')

        caps = point_layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddFeatures:
            point_layer.startEditing()
            for i, kp in enumerate(kp1):
                feat = QgsFeature(point_layer.fields())
                x, y = self.local2src(kp.pt[0], kp.pt[1], sdp)
                feat.setAttributes([x, y, kp.size, kp.angle, kp.response, kp.octave])

                geom = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                feat.setGeometry(geom)
                _ = point_layer.dataProvider().addFeatures([feat])
            point_layer.commitChanges()

        else:
            print("Error")
            return {}

        return point_layer

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        feedback = QgsProcessingMultiStepFeedback(11, feedback)
        results = {}
        outputs = {}

        source = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        sourceNoBosco = self.parameterAsRasterLayer(parameters, self.INPUT_NOBOSCO, context)
        sourceSiBosco = self.parameterAsRasterLayer(parameters, self.INPUT_SIBOSCO, context)
        temppathfile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        outputKeyPoints = self.parameterAsVectorLayer(parameters, "keypoints", context)

        # ret, markers = cv.connectedComponents(sure_fg)
        # https://docs.opencv.org/4.x/d3/db4/tutorial_py_watershed.html
        ksize = parameters['larghezza_minima_m']/source.rasterUnitsPerPixelX()
        minArea = parameters['area_minima_m2']
        ksizeGaps = math.sqrt(parameters['area_minima_m2'] / 3.14)
        areaPixel = source.rasterUnitsPerPixelX()*source.rasterUnitsPerPixelX()
        feedback.setProgressText("Preparo il raster in output")
        pipe = QgsRasterPipe()
        sdp = source.dataProvider()
        if source.bandCount() != 1:
            feedback.reportError('Il raster CHM deve avere solamente una banda - il file ' +
                                 str(source.source()) + ' ha ' + str(source.bandCount()) + ' bande!'
                                 )
            return {}

        pipe.set(sdp.clone())

        rasterWriter = QgsRasterFileWriter(temppathfile)
        error = rasterWriter.writeRaster(pipe, sdp.xSize(), sdp.ySize(), sdp.extent(), sdp.crs())

        if error == QgsRasterFileWriter.NoError:
            print("Output preparato con successo!")
        else:
            feedback.reportError('Non sono riuscito ad implementare il raster nuovo OPENING - ' + str(temppathfile))
            return {}

        feedback.setProgressText("Creo il raster temporaneo " + temppathfile+ " di tipo " +  str(source.dataProvider().bandScale(0)))
        tempRasterLayer = QgsRasterLayer(temppathfile)
        provider = tempRasterLayer.dataProvider()
        feedback.setProgressText("reato il raster temporaneo " + provider.name() + " di tipo " +  str(source.dataProvider().bandScale(0)) + " -- - " + str( provider.xSize()) + " x " + str(provider.ySize()))
        block = provider.block(1, provider.extent(), provider.xSize(), provider.ySize())

        if provider is None:
            feedback.reportError('Cannot find or read ' + tempRasterLayer.source())
            return {}

        feedback.setProgressText("Leggo il raster")

        ds = gdal.Open(str(source.source()))
        img =  np.array(ds.GetRasterBand(1).ReadAsArray())
        feedback.setProgressText("Letto raster di dimensioni "+ str(img.shape))
        #img = cv.imread(source.source(), cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE )  #cv.IMREAD_GRAYSCALE
        if img is None:
            feedback.reportError('Errore nella lettura con opencv del CHM ' + source.source())
            return {}

        feedback.reportError(str(img.shape))

        # Check for cancelation
        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Dimensione immagine: " + ' x '.join(map(str, img.shape)))
        feedback.setProgressText("Applico soglia di altezza di : " +
                                 str(parameters['altezza_alberochioma_m']) + ' metri ')
        # binarize the image
        binr = cv.threshold(img, parameters['altezza_alberochioma_m'], 1, cv.THRESH_BINARY)[1]

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        feedback.setProgressText("Creo un kernel di : " + str(round(ksize, 3)) +
                                 '(' + str(int(ksize)) +
                                 ') metri  e larghezza minima ' + str(parameters['larghezza_minima_m']))

        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (int(ksize), int(ksize)))
        # Check for cancelation
        if feedback.isCanceled():
            return {}

        feedback.setProgressText("Processo Dilate raster")
        closing = cv.morphologyEx(binr, cv.MORPH_CLOSE, kernel)
        if feedback.isCanceled():
            return {}

        feedback.setProgressText("Processo Erode  raster")
        opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernel)
        if feedback.isCanceled():
            return {}

        feedback.setProgressText("Processo Invert raster")
        binr = ((opening - 1) * -1).astype('B')

        #opening = cv.distanceTransform(binr, cv.DIST_L2, 3)
        feedback.setProgressText("Processo contour raster")
        contours, _ = cv.findContours(binr, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for i in range(len(contours)):
            aa = int(cv.contourArea(contours[i])*areaPixel )
            if aa < minArea:
                cv.drawContours(opening, contours, i, 1, -1)
            else:
                cv.drawContours(opening, contours, i, 0, -1)

        #closing = cv.morphologyEx(binr, cv.MORPH_CLOSE, kernel)
       # opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernel)

        #opening = cv.morphologyEx( cv.morphologyEx(binr, cv.MORPH_OPEN, kernel) , cv.MORPH_CLOSE, kernel)
        # Check for cancelation


        if sourceSiBosco is not None:
            if sourceSiBosco.bandCount() != 1:
                feedback.reportError('Troppe bande ('+ str(sourceSiBosco.bandCount()) +
                                     ') nel raster Bosco letto dal file' +
                                     sourceSiBosco.source())
                return {}
            imgSiBosco = cv.imread(sourceSiBosco.source(), cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE )  #cv.IMREAD_GRAYSCALE
            if imgSiBosco is None:
                feedback.reportError('Errore nella lettura con opencv del raster Bosco ' + sourceSiBosco.source())
                return {}
            opening = opening * (imgSiBosco != 0)
        if sourceNoBosco is not None:
            if sourceNoBosco.bandCount() != 1:
                feedback.reportError('Troppe bande ('+
                                     str(sourceNoBosco.bandCount())+') nel raster No-Bosco letto dal file' + sourceNoBosco.source())
                return {}
            imgNoBosco = cv.imread( sourceNoBosco.source(), cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE )  #cv.IMREAD_GRAYSCALE
            if imgNoBosco is None:
                feedback.reportError('Errore nella lettura con opencv del raster No-Bosco ' + sourceNoBosco.source())
                return {}

            opening = opening * (imgNoBosco == 0)

        #opening[opening == 0] = np.NaN
        provider.setEditable(True)
        data = bytearray(bytes(opening))
        block.setData(data)
        block.setNoDataValue(0)
        writeok = provider.writeBlock(block, 1)
        if writeok:
            feedback.setProgressText("Successo nella scrittura del dato")
        else:
            feedback.setProgressText("Non sono riuscito a scrivere il blocco raster")
            return {}

        provider.setEditable(False)

        out_rlayer = QgsRasterLayer(temppathfile, "Area Foresta hTrees="+
                                    str(parameters['altezza_alberochioma_m']) +
                                    " k="+str(int(ksize)) )

        mess, success = out_rlayer.loadNamedStyle(dirname+"/extra/style.qml")
        if success is False:
            feedback.setProgressText( mess + " - " + dirname+"/extra/style.qml")
        else:
            feedback.setProgressText( mess)

        QgsProject.instance().addMapLayer(out_rlayer)
        #self.iface.mapCanvas().refresh()

        feedback.setProgressText(tempRasterLayer.source())



        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        #return {self.OUTPUT: temppathfile}
        return results
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'CHM => Bosco'

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
