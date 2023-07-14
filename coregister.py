# -*- coding: utf-8 -*-

"""
/***************************************************************************
 CHMtoForest
                                 A QGIS plugin
 Converts a CHM to a raster layer with forest polygons according to various definitions
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
from datetime import datetime
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
class CoRegister(QgsProcessingAlgorithm):
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

    INPUT_REGISTER = 'INPUT_REGISTER'
    INPUT_REFERENCE = 'INPUT_REFERENCE'
    KEYPOINTS = 'keypoints'
    timePre = datetime.now()
    timePost = datetime.now()
    totTime = (timePost - timePre).total_seconds()
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_REGISTER,
                self.tr('Input Register')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_REFERENCE,
                self.tr('Input Reference')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                'maxPoints',
                self.tr('Numero massimo di punti'),
                defaultValue=2.0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink('Features',
                                            self.KEYPOINTS,
                                            type=QgsProcessing.TypeVectorPoint,
                                            createByDefault=True,
                                            defaultValue=None)
        )


    #def icon(self):
        #cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        #icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        #return icon
    def getTimePassed(self, feedback, message=None):
        self.timePost = datetime.now()
        self.timeDiff = (self.timePost-self.timePre)
        if message is not None:
            feedback.setProgressText("Time passed: " + str(self.timeDiff) + " for " + message)
        else:
            feedback.setProgressText("Time passed: " + str(self.timeDiff) )
        self.totTime += self.timeDiff.total_seconds()
        self.timePre = datetime.now()
    def local2src(self, x, y, dataProvider, ext, xres, yres, verbose=False ):
        x1 = 0
        y1 = 0
        if isinstance(dataProvider, QgsRasterDataProvider):

            x1 = ext.xMinimum() + float(x) * xres + xres/2.0
            y1 = ext.yMaximum() - float(y) * yres - yres/2.0
            if verbose:
                print( str(x) + ' - ' + str(x1)   )

        return x1, y1

    def _create_points(self, kp1, sdp, feedback ):
        """Create points for testing"""

        srcCRS = sdp.crs()
        point_layer = QgsVectorLayer('Point?crs=EPSG:4326', 'keypoints', 'memory')
        point_layer.setCrs(srcCRS)
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
            ext = QgsRectangle(sdp.extent())
            xres= (ext.xMaximum() - ext.xMinimum()) / sdp.xSize()
            yres= (ext.yMaximum() - ext.yMinimum()) / sdp.ySize()
            cnt = 0

            every = int(len(kp1)/100)
            for i, kp in enumerate(kp1):
                cnt += 1
                if every > 100:
                    if cnt % every == 0:
                        feedback.setProgress(int(cnt/len(kp1)*100))
                        if feedback.isCanceled():
                            return None
                    if cnt % (every*10) == 0:
                        feedback.setProgressText(str(round(cnt/len(kp1)*100)) + "% ....")

                feat = QgsFeature(point_layer.fields())
                x, y = self.local2src(kp.pt[0], kp.pt[1], sdp, ext, xres, yres)
                feat.setAttributes([x, y, kp.size, kp.angle, kp.response, kp.octave])

                geom = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                feat.setGeometry(geom)
                _ = point_layer.dataProvider().addFeatures([feat])
            point_layer.commitChanges()

        else:
            print("Error")
            return {}

        return point_layer

    def matchPoints(self, des1, des2, kps1, kps2, img1, img2):
        min_match=10
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)

        flann = cv.FlannBasedMatcher(index_params, search_params)
        # Create a feature matcher
        #matcher = cv.BFMatcher()

        # Match descriptors of the two images
        #matches = matcher.match(des1, des2)
        #matches = sorted(matches, key=lambda x: x.distance)
        #good_matches = matches[:50]  # Adjust the number of matches based on your needs

        # Extract matched keypoints
        #src_pts = np.float32([kps1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        #dst_pts = np.float32([kps2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Estimate transformation matrix (homography) using RANSAC
        #homography, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
        #rotation = cv.RQDecomp3x3(homography[:3, :3])[0]
        #translation = homography[:, 2]

        matches = flann.knnMatch(des1, des2, k=2)

        # store all the good matches (g_matches) as per Lowe's ratio
        g_match = []
        for m,n in matches:
            if m.distance < 0.7 * n.distance:
                g_match.append(m)
        if len(g_match)>min_match:
            src_pts = np.float32([ kps1[m.queryIdx].pt for m in g_match ]).reshape(-1,1,2)
            dst_pts = np.float32([ kps2[m.trainIdx].pt for m in g_match ]).reshape(-1,1,2)

            M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()

            h,w = img1.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv.perspectiveTransform(pts,M)

            img2 = cv.polylines(img2, [np.int32(dst)], True, (0,255,255) , 3, cv.LINE_AA)

        else:
            print("Not enough matches have been found! - %d/%d" % (len(g_match), min_match))
            matchesMask = None

        draw_params = dict(matchColor = (0,255,255),
                           singlePointColor = (0,255,0),
                           matchesMask = matchesMask, # only inliers
                           flags = 2)
        # region corners
        cpoints = np.int32(dst)
        a, b, c = cpoints.shape

        # reshape to standard format
        c_p = cpoints.reshape((b, a, c))

        # crop matching region
        matching_region = crop_region(path_train, c_p)

        img3 = cv.drawMatches(img1, kps1, img2, kps2, g_match, None, **draw_params)
        return (img3, matching_region)

    def crop_region(self, path, c_p):
        """
          This function crop the match region in the input image
          c_p: corner points
        """
        # 3 or 4 channel as the original
        img = cv.imread(path, -1)

        # mask
        mask = np.zeros(img.shape, dtype=np.uint8)

        # fill the the match region
        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
        cv.fillPoly(mask, c_p, ignore_mask_color)

        # apply the mask
        matched_region = cv.bitwise_and(img, mask)

        return matched_region
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        feedback = QgsProcessingMultiStepFeedback(11, feedback)
        results = {}
        outputs = {}
        start = datetime.now()
        source = self.parameterAsRasterLayer(parameters, self.INPUT_REGISTER, context)
        reference = self.parameterAsRasterLayer(parameters, self.INPUT_REFERENCE, context)
        outputKeyPoints = self.parameterAsVectorLayer(parameters, self.KEYPOINTS, context)

        feedback.setProgressText("Leggo il raster")
        try:
            ds = gdal.Open(str(source.source()))
        except:
            feedback.reportError('Non sono riuscito a leggere il raster CHM ' +
                                 gdal.GetLastErrorMsg() )
            return {}

        img = np.array(ds.GetRasterBand(1).ReadAsArray())
        feedback.setProgressText("Convert to 8 bit")
        img8bit = (img*10).astype('B')
        if img is None:
            feedback.reportError('Errore nella lettura con opencv del CHM ' + source.source())
            return {}

        # Initiate ORB detector
        orb = cv.ORB_create()
        sift = cv.SIFT_create()
        feedback.setProgressText("Preparing SIFT... might take time for large images (e.g. 40 s on a 4000 x 5000 pixel image)")
        kps, des = sift.detectAndCompute(img8bit, None)
        self.getTimePassed(feedback, "SIFT with " + str(len(kps)) + " points")
        outputKeyPoints = self._create_points(kps, source.dataProvider(), feedback)
        QgsProject.instance().addMapLayer(outputKeyPoints)
        # find the keypoints with ORB
        kp = orb.detect(img8bit, None)
        self.getTimePassed(feedback, "ORB with " + str(len(kp)) + " points")
        kp, des = orb.compute(img8bit, kp)
        self.getTimePassed(feedback, "ORB2 with " + str(len(kp)) + " points")

        feedback.setProgressText("Letto raster di dimensioni "+ str(img.shape))
        # Check for cancelation
        if feedback.isCanceled():
            return {}
        return results
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'CHM => Co-Registra'

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
        return CoRegister()
