# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RNCLoader
                                 A QGIS plugin
 Lists Raster Nautical Charts by title.
                              -------------------
        begin                : 2016-10-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Roland Arsenault
        email                : roland@rolker.net
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QStandardItemModel
from PyQt4.QtGui import QStandardItem, QSortFilterProxyModel

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from rnc_loader_dialog import RNCLoaderDialog
import os.path
import glob


class RNCLoader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RNCLoader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RNC Loader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RNCLoader')
        self.toolbar.setObjectName(u'RNCLoader')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RNCLoader', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = RNCLoaderDialog()
        self.dlg.pushButton.clicked.connect(self.selectRootDirectory)
        self.chartModel = QStandardItemModel(self.dlg.chartListView)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setDynamicSortFilter(True)
        self.filterModel.setFilterCaseSensitivity(False)
        self.filterModel.setSourceModel(self.chartModel)
        self.dlg.chartListView.setModel(self.filterModel)
        self.dlg.filterLineEdit.textChanged.connect(
            self.filterModel.setFilterWildcard)

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
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RNCLoader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Load RNC'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&RNC Loader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def selectRootDirectory(self):
        filename = QFileDialog.getExistingDirectory(
            self.dlg, "Select base directory ", self.dlg.rncRootLabel.text())
        self.dlg.rncRootLabel.setText(filename)
        QSettings().setValue('RNCLoader/rnc_root', filename)
        self.scanCharts(rootdir)

    def scanCharts(self, rootdir):
        bsbs = glob.glob(os.path.join(rootdir, '*/*.BSB'))
        self.charts = []
        for b in bsbs:
            for l in open(b).readlines():
                if l.startswith('K'):
                    parts = l.strip().split('/')[1].split(',')
                    items = {}
                    for p in parts:
                        k, v = p.split('=', 1)
                        items[k] = v
                    if 'FN' in items:
                        self.charts.append(
                            (items['NA'], os.path.join(os.path.dirname(b),
                                 items['FN']), items['FN']))
        self.listCharts()

    def listCharts(self):

        self.chartModel.clear()
        for c in self.charts:
            item = QStandardItem(c[0] + ' (' + c[2] + ')')
            item.setData(c[1])
            self.chartModel.appendRow(item)

    def run(self):
        """Run method that performs all the real work"""

        rnc_root = QSettings().value('RNCLoader/rnc_root', '~/')
        self.dlg.rncRootLabel.setText(rnc_root)
        self.scanCharts(rnc_root)

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            selected = self.dlg.chartListView.selectedIndexes()
            for i in selected:
                item = self.chartModel.itemFromIndex(
                    self.filterModel.mapToSource(i))
                self.iface.addRasterLayer(item.data())
