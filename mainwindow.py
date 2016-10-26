import pickle
import sys
import time

from PyQt5.QtCore import Qt, pyqtSlot, QSettings, QPoint
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import *
from camera.cameraconfigwidget import *
from camera.cameradaemon import *

from camera.camerawidget import CameraWidget
from settingsform import SettingsDialog, ErrorHandlingModes


def printState(state, old):
    print("Cam State: {0} -> {1}".format(old, state))

def printError(msg):
    print(msg, file=sys.stderr)


class MainWindow(QMainWindow):
    # initialization time in ms
    STARTUP_TIME = 0.2

    def __init__(self):
        QMainWindow.__init__(self)

        settings = QSettings("UBC", "Arpes")

        settings.beginGroup("ErrorHandling")
        self.errorMode = settings.value("errorMode", ErrorHandlingModes.Default.value)
        settings.endGroup()

        # self.setupUI()


        self.createActions()

        self.docks = []

        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.logDock = QDockWidget("Log", self)
        self.logDock.setWidget(self.log)
        self.logDock.setObjectName('Log')
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logDock)

        self.panel = CenterPanel(self)
        self.setCentralWidget(self.panel)
        self.loadSettings()
        # self.setupCamDaemon()
        self.setObjectName('MainWindow')
        self.setWindowTitle('XUV Control Application')


        # time.sleep(self.STARTUP_TIME)
        self.show()


    def createActions(self):
        self.fileMenu = self.menuBar().addMenu("File")

        self.quitAct = self.fileMenu.addAction("&Quit", self.close)
        self.quitAct.setShortcuts(QKeySequence.Quit)
        self.quitAct.setStatusTip("Quit the application")

        self.viewMenu = self.menuBar().addMenu("View")
        self.menuBar().addSeparator()

        self.toolsMenu = self.menuBar().addMenu("Tools")
        editSettingsAct = QAction("Settings", self)
        editSettingsAct.setIcon(QIcon('resources/gear.png'))
        editSettingsAct.triggered.connect(self.editSettings)
        self.toolsMenu.addAction(editSettingsAct)

        self.helpMenu = self.menuBar().addMenu("Help")
        aboutAct = self.helpMenu.addAction("About", self.about)
        aboutAct.setStatusTip("Show the application's About box")
        aboutQtAct = self.helpMenu.addAction("About Qt", QApplication.aboutQt)
        aboutQtAct.setStatusTip("Show the Qt library's About box")


    def addDockWidget(self, area, dockwidget, orientation=Qt.Horizontal):
        QMainWindow.addDockWidget(self, area, dockwidget, orientation)
        self.viewMenu.addAction(dockwidget.toggleViewAction())
        self.docks.append(dockwidget)

    def removeDockWidget(self, dockwidget):
        dockwidget.hide()
        QMainWindow.removeDockWidget(self, dockwidget)
        self.docks.remove(dockwidget)
        self.viewMenu.removeAction(dockwidget.toggleViewAction())


    def about(self):
        QMessageBox.about(self, "About XUV Control Application",
                          "This application controls experimental devices important for XUV Laser spectroscopy in David Jone's Lab.");


    @pyqtSlot(str, ErrorPriority)
    def processError(self, msg, priority):
        if(priority.value >= ErrorPriority.Critical.value) and self.errorMode <= ErrorHandlingModes.Verbose.value:
            QErrorMessage.qtHandler().showMessage('Camera Error: ' + msg)
        if self.errorMode < ErrorHandlingModes.Disabled.value:
            print(msg, file=sys.stderr)
            if priority.value >= ErrorPriority.Critical.value:
                msg = time.strftime('<b>[%a, %d %b %Y %H:%M:%S, %z] (', time.gmtime()) + priority.name + ") </b>: " + msg
            else:
                msg = '(' + priority.name + ') : ' + msg
            self.log.append(msg + '\n')


    @pyqtSlot(bool)
    def editSettings(self, bool):
        settings = QSettings("UBC", "Arpes")

        settings.beginGroup("ErrorHandling")
        errorMode = settings.value("errorMode", ErrorHandlingModes.Default.value)
        settings.endGroup()

        settings.beginGroup("SaveLoad")
        saveGeo = settings.value("saveGeo", True) == 'true'
        saveProps = settings.value("saveProps", True) == 'true'
        saveConfig = settings.value("saveConfig", True) == 'true'
        settings.endGroup()

        settingsForm = SettingsDialog(errorMode, saveGeo, saveProps, saveConfig, self)

        if(settingsForm.exec() == QMessageBox.Accepted):
            settings = QSettings("UBC", "Arpes")

            settings.beginGroup("ErrorHandling")
            self.errorMode = settingsForm.errorCombo.currentIndex()
            settings.setValue("errorMode", self.errorMode)
            settings.endGroup()

            settings.beginGroup("SaveLoad")
            settings.setValue("saveGeo", settingsForm.saveGeoCheck.isChecked())
            settings.setValue("saveProps", settingsForm.savePropsCheck.isChecked())
            settings.setValue("saveConfig", settingsForm.saveConfigCheck.isChecked())
            settings.endGroup()
        else:
            pass #do nothing

    def writeSettings(self):
        settings = QSettings("UBC", "Arpes")

        settings.beginGroup("ErrorHandling")
        settings.setValue("errorMode", self.errorMode)
        settings.endGroup()

        settings.beginGroup("SaveLoad")
        saveGeo = settings.value("saveGeo", True) == 'true'
        saveProps = settings.value("saveProps", True) == 'true'
        saveConfig = settings.value("saveConfig", True) == 'true'
        settings.endGroup()

        if(saveGeo):
            settings.beginGroup("MainWindow")
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("windowState", self.saveState())
            settings.endGroup()
            settings.beginGroup("Center")
            settings.setValue("Name", self.panel.currentWidget.objectName())
            settings.endGroup()

        for camWidget in CameraWidget.camlist:
            settings.beginGroup(camWidget.objectName())

            if (saveProps):
                if camWidget.camPropWidget.initialized:
                    settings.beginGroup("CamProps")
                    for camWidget in CameraWidget.camlist:
                        props = camWidget.camPropWidget.properties
                        arr = pickle.dumps(props)
                        settings.setValue("props", arr)
                    settings.endGroup()

            if saveConfig:
                settings.beginGroup("CamConfig")
                config = camWidget.cameraConfigWidget.cam_config
                for k, v in config.items():
                    settings.setValue(k, v)
                settings.endGroup()

            settings.endGroup()

    def loadSettings(self):
        settings = QSettings("UBC", "Arpes")

        settings.beginGroup("ErrorHandling")
        self.errorMode = settings.value("errorMode", ErrorHandlingModes.Default.value)
        settings.endGroup()

        settings.beginGroup("SaveLoad")
        saveGeo = settings.value("saveGeo", True)
        saveProps = settings.value("saveProps", True)
        saveConfig = settings.value("saveConfig", True)
        settings.endGroup()

        settings.beginGroup("Cameras")
        arr = settings.value('List')

        if arr:
            camlist = pickle.loads(arr)
            for name in camlist:
                cameraWidget = CameraWidget(self, name)
                camDock = QDockWidget(cameraWidget.objectName(), self)
                camDock.setWidget(cameraWidget)
                camDock.setObjectName(cameraWidget.objectName())
                self.addDockWidget(Qt.RightDockWidgetArea, camDock)
        else:
            self.cameraWidget = CameraWidget(self)
            camDock = QDockWidget(self.cameraWidget.objectName(), self)
            camDock.setWidget(self.cameraWidget)
            camDock.setObjectName(self.cameraWidget.objectName())
            self.addDockWidget(Qt.RightDockWidgetArea, camDock)
        settings.endGroup()

        if saveGeo:
            settings.beginGroup("MainWindow")
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            state = settings.value("windowState")
            if state:
                self.restoreState(state)
            settings.endGroup()
            settings.beginGroup("Center")
            name = settings.value("Name")
            if name:
                if name == 'Blank':
                    self.panel.setToBlank()
                else:
                    dockwidget = self.findChild(QDockWidget, name)
                    if dockwidget:
                        widget = dockwidget.widget()
                        widget.setObjectName(name)
                        self.panel.setCurrentWidget(widget)
                        self.panel.setTitle(name)
                        self.removeDockWidget(dockwidget)
            settings.endGroup()

        for camWidget in CameraWidget.camlist:
            settings.beginGroup(camWidget.objectName())

            if saveProps and camWidget.camPropWidget.initialized:
                settings.beginGroup("CamProps")
                arr = settings.value("props")
                if arr:
                    props = pickle.loads(arr)
                    camWidget.camPropWidget.properties = props
                    camWidget.camPropWidget.setAllProperties()
                    camWidget.camPropWidget.revertSavedProperties()
                settings.endGroup()

            if saveConfig:
                settings.beginGroup("CamConfig")
                config = camWidget.cameraConfigWidget.cam_config
                reload = False
                for k, v in config.items():
                    val = settings.value(k)
                    if val:
                        config[k] = val
                        reload = True
                if reload:
                    camWidget.cameraConfigWidget.reloadConfigData()
                settings.endGroup()

            settings.endGroup()

    def addNewCamera(self, id):
        """
        Adds a new camera widget
        :param id: string identifier for the camera
        :return:
        """
        cameraWidget = CameraWidget(self, id)
        dock = QDockWidget(cameraWidget.objectName(), self)
        dock.setWidget(cameraWidget)
        dock.setObjectName(cameraWidget.objectName())
        self.addDockWidget(Qt.RightDockWidgetArea, dock)


    def removeCamera(self):
        cameraWidget = self.sender()
        cameraWidget.stopStreaming()
        time.sleep(0.5)
        if self.panel.currentWidget == cameraWidget:
            dock = self.panel.setToBlank()
            if dock:
                self.removeDockWidget(dock)

        else:
            dock = cameraWidget.parent()
            self.removeDockWidget(dock)
        cameraWidget.deleteLater()


    def closeEvent(self, event):
        self.writeSettings()
        event.accept()


class CenterPanel(QGroupBox):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.layout = QVBoxLayout()
        self.currentWidget = QFrame(self)
        self.currentWidget.setObjectName('Blank')
        self.layout.addWidget(self.currentWidget)
        self.setLayout(self.layout)
        self.setStyleSheet('QGroupBox { margin: 2px; border: 2px solid gray; border-width: 2px; border-style: outset }')

    def setCurrentWidget(self, widget):
        main = self.parent()
        if self.currentWidget.objectName() == 'Blank':
            self.layout.removeWidget(self.currentWidget)
            self.currentWidget = widget
            self.layout.addWidget(widget)
        else:
            # pop out the current widget into a dock widget
            self.layout.removeWidget(self.currentWidget)
            main = self.parent()
            dock = QDockWidget(self.currentWidget.objectName(), main)
            dock.setWidget(self.currentWidget)
            dock.setObjectName(self.currentWidget.objectName())
            main.addDockWidget(Qt.RightDockWidgetArea, dock)

            # insert new widget
            self.currentWidget = widget
            self.layout.addWidget(self.currentWidget)


    def setToBlank(self):
        if self.currentWidget.objectName() == 'Blank':
            return
        else:
            # pop out the current widget into a dock widget
            self.layout.removeWidget(self.currentWidget)
            main = self.parent()
            dock = QDockWidget(self.currentWidget.objectName(), main)
            dock.setWidget(self.currentWidget)
            dock.setObjectName(self.currentWidget.objectName())
            main.addDockWidget(Qt.RightDockWidgetArea, dock)

            blank = QFrame()
            blank.setObjectName('Blank')
            self.layout.addWidget(blank)
            self.currentWidget = blank
            self.setTitle('')

            return dock

    def isBlank(self):
        return isinstance(self.currentWidget, QFrame)


    @pyqtSlot(QPoint)
    def showContextMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        main = self.parent()

        menu = QMenu()

        submenu = QMenu('Set Widget')
        for dockwidget in main.docks:
            submenu.addAction(dockwidget.objectName())
        menu.addMenu(submenu)

        setBlankAction = QAction("Set as blank", self)
        if self.currentWidget.objectName() != 'Blank':
            menu.addAction(setBlankAction)

        selectedItem = menu.exec(globalPos)

        if selectedItem:
            if selectedItem == setBlankAction:
                self.setToBlank()
            else:
                name = selectedItem.text()
                for dockwidget in main.docks:
                    if dockwidget.objectName() == name:
                        self.setCurrentWidget(dockwidget.widget())
                        self.setTitle(name)
                        self.currentWidget.setObjectName(name)
                        main.removeDockWidget(dockwidget)
                        break
        else:
            # nothing was chosen
            pass






