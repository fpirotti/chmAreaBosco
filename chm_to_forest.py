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

import os
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .chm_to_forest_provider import CHMtoForestProvider

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import processing

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class CHMtoForestPlugin(object):

    def __init__(self, iface):
        self.provider = None
        self.iface = iface

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = CHMtoForestProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        icon = os.path.join(os.path.join(cmd_folder, 'logo.png'))
        self.action = QAction(
             QIcon(icon),
             u"CHM => Bosco", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu(u"&Reg. Veneto Servizio Foreste", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        self.iface.removePluginMenu(u"&Reg. Veneto Servizio Foreste", self.action)
        self.iface.removeToolBarIcon(self.action)
    def run(self):
        processing.execAlgorithmDialog("Reg. Veneto Servizio Foreste:CHM => Bosco")