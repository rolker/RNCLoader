# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RNCLoader
                                 A QGIS plugin
 Lists Raster Nautical Charts by title.
                             -------------------
        begin                : 2016-10-06
        copyright            : (C) 2016 by Roland Arsenault
        email                : roland@rolker.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RNCLoader class from file RNCLoader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rnc_loader import RNCLoader
    return RNCLoader(iface)
