import time

from PyQt5.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QVideoSurfaceFormat, QVideoFrame
from PyQt5.QtWidgets import *
from camera.cameraconfigwidget import *
from camera.cameradaemon import *
from camera.camerainfowidget import CameraInfoWidget

from camera.camerapropwidget import CameraPropertiesWidget
from camera.viewfinderwidget import ViewfinderWidget


class CameraWidget(QWidget):

    def __init__(self, parent=None, name=''):
        super().__init__(parent)

        if parent:
            self.main = parent # first parent is always the mainwindow
        else:
            return

        self.setObjectName('Camera View')

        self.setupUI()
        self.setupView()
        self.setupCamDaemon()


    def deleteLater(self):
        self.camD.disconnect()
        self.camD.deleteLater()

        self.main.removeDockWidget(self.camConfigDock)
        self.cameraConfigWidget.deleteLater()

        self.main.removeDockWidget(self.camInfoDock)
        self.cameraInfo.deleteLater()

        self.main.removeDockWidget(self.histoDock)

        self.main.removeDockWidget(self.camPropDock)
        self.camPropWidget.deleteLater()

        QWidget.deleteLater(self)


    def setupUI(self):
        self.cameraConfigWidget = CameraConfigureWidget(self)
        self.camConfigDock = QDockWidget("Camera Configuration", self)
        self.camConfigDock.setWidget(self.cameraConfigWidget)
        self.camConfigDock.setObjectName("Camera Configuration")
        self.main.addDockWidget(Qt.BottomDockWidgetArea, self.camConfigDock)

        self.cameraInfo = CameraInfoWidget(self)
        self.camInfoDock = QDockWidget("Camera Info", self)
        self.camInfoDock.setWidget(self.cameraInfo)
        self.camInfoDock.setObjectName("Camera Info")
        self.main.addDockWidget(Qt.BottomDockWidgetArea, self.camInfoDock)

        self.camPropWidget = CameraPropertiesWidget(self)
        self.camPropDock = QDockWidget("Camera Properties", self)
        self.camPropDock.setWidget(self.camPropWidget)
        self.camPropDock.setObjectName("Camera Properties")
        self.main.addDockWidget(Qt.RightDockWidgetArea, self.camPropDock)

        self.cameraConfigWidget.erroredOut.connect(self.main.processError)
        self.cameraConfigWidget.cameraConfigChanged.connect(self.changeCameraConfig)

    def setupView(self):
        self.camView = ViewfinderWidget(self)


        self.toolBar = QToolBar('Camera')
        lbl = QLabel("<b>Camera Controls</b>:")
        self.toolBar.addWidget(lbl)
        playIcon = QIcon('resources/button_blue_play.png')
        self.playAct = QAction(playIcon, "Play", self)
        self.playAct.setToolTip("Start camera strean")
        stopIcon = QIcon('resources/button_blue_stop.png')
        self.stopAct = QAction(stopIcon, "Stop", self)
        self.stopAct.setToolTip("Stop camera stream")
        self.toolBar.addAction(self.playAct)
        self.toolBar.addAction(self.stopAct)
        camPropIcon = QIcon('resources/aperture.png')
        self.toggleCamPropAct = self.camPropDock.toggleViewAction()
        self.toggleCamPropAct.setIcon(camPropIcon)
        self.toggleCamPropAct.setToolTip("Show/Hide Camera Properties")
        self.toolBar.addAction(self.toggleCamPropAct)
        self.toolBar.addSeparator()
        self.toolBar.setObjectName("Camera Controls")

        self.statusIcons = dict()
        self.statusIcons['Streaming'] = ('resources/status_green.png')
        self.statusIcons['Connected'] = ('resources/status_away.png')
        self.statusIcons['Disconnected'] = ('resources/status_offline.png')
        self.statusIcons['Invalid'] = ('resources/status_busy.png')

        self.camStatusLbl = QLabel()
        self.camStatusLbl.setText("<b>Status</b>:    Disconnected")
        self.toolBar.addWidget(self.camStatusLbl)

        self.camStatusIcon = QLabel()
        self.camStatusIcon.setTextFormat(Qt.RichText)
        self.camStatusIcon.setText("<img src=\"" + self.statusIcons['Disconnected'] + "\">")
        self.toolBar.addWidget(self.camStatusIcon)

        self.toolBar.addSeparator()
        lbl = QLabel("<b>Camera Configuration:</b>")
        self.toolBar.addWidget(lbl)
        camRestartIcon = QIcon('resources/camera_reload.png')
        self.restartCamAct = QAction(camRestartIcon, "Restart Camera", self)
        self.restartCamAct.setToolTip("Re-configure and restart camera stream")
        self.toolBar.addAction(self.restartCamAct)
        camConfigIcon = QIcon('resources/camera_gear.png')
        self.toggleCamConfigAct = self.camConfigDock.toggleViewAction()
        self.toggleCamConfigAct.setIcon(camConfigIcon)
        self.toggleCamConfigAct.setToolTip("Show/Hide Camera Configuration")
        self.toolBar.addAction(self.toggleCamConfigAct)

        self.toolBar.addSeparator()
        lbl = QLabel("<b>Camera Info:</b>")
        self.toolBar.addWidget(lbl)
        camInfoIcon = QIcon('resources/camera_info.png')
        self.toggleCamInfoAct = self.camInfoDock.toggleViewAction()
        self.toggleCamInfoAct.setIcon(camInfoIcon)
        self.toggleCamInfoAct.setToolTip("Show/Hide Camera Info")
        self.toolBar.addAction(self.toggleCamInfoAct)

        self.playAct.triggered.connect(self.startStreaming)
        self.stopAct.triggered.connect(self.stopStreaming)
        self.restartCamAct.triggered.connect(self.restartCamStream)





        vbox = QVBoxLayout()
        vbox.addWidget(self.toolBar)
        vbox.addWidget(self.camView)


        self.setLayout(vbox)


    def setupCamDaemon(self):
        config = self.cameraConfigWidget.cam_config

        format = QVideoSurfaceFormat(QSize(config['cam_w'], config['cam_h']), QVideoFrame.Format_RGB24)

        self.camD = PGCameraDaemon(parent=self, **config,
                              cam_pixformat=fc2.PIXEL_FORMAT_RGB8)

        self.cameraInfo.updateCamConfig(config)

        self.camD.receivedFrame.connect(self.camView.processFrame)
        self.camD.stateChanged.connect(self.updateCamStatus)
        self.camD.erroredOut.connect(self.main.processError)
        self.camD.camConnected.connect(self.cameraInfo.updateCamInfo)
        self.camD.camConnected.connect(self.updateViewToolTip)

        if(self.camD.state == PGCameraStates.Connected or self.camD.state == PGCameraStates.Streaming):
            self.camPropWidget.setupUI(self.camD)
        else:
            self.camPropDock.close()
            self.toggleCamPropAct.setChecked(False)
            self.toggleCamPropAct.setEnabled(False)

        self.camD.receivedFrame.connect(self.camPropWidget.refreshProperties)


        # time.sleep(0.5)

        self.startStreaming()

        # time.sleep(0.2)


    def emitNewCameraRequest(self):
        newName, ok = QInputDialog.getText(self.parent(), "New Camera Request", "Enter new Camera ID (leave blank for default):")
        if ok:
            self.addCameraRequested.emit(newName)
        else:
            pass

    def emitRemoveCameraRequest(self):
        self.removeCameraRequested.emit()

    @pyqtSlot(dict)
    def changeCameraConfig(self, config):
        """

        :param config: dictionary containing configuration values
        :return:
        """
        self.cameraInfo.updateCamConfig(config)
        self.camD.changeCameraConfig(**config)
        self.camView.setToolTip(self.cameraInfo.getRichText())
        fr = self.camD.getFrameRate()

        # -1 indicates error
        if fr == -1 or fr is None:
            return
        else:
            self.camView.FRAME_RATE = fr

    @pyqtSlot(PGCameraStates, PGCameraStates)
    def updateCamStatus(self, newState, oldState):
        self.camStatusLbl.setText("<b>Status</b>:    " + newState.name)
        self.camStatusIcon.setText("<img src=\"" + self.statusIcons[newState.name] + "\">")

        if (self.camD.state == PGCameraStates.Streaming):
            self.playAct.setEnabled(False)
            self.stopAct.setEnabled(True)
            self.toggleCamPropAct.setEnabled(True)
            if (not self.camPropWidget.initialized):
                self.camPropWidget.setupUI(self.camD)
        elif self.camD.state == PGCameraStates.Connected:
            self.playAct.setEnabled(True)
            self.stopAct.setEnabled(False)
            self.toggleCamPropAct.setEnabled(True)
            if (not self.camPropWidget.initialized):
                self.camPropWidget.setupUI(self.camD)
        else:
            self.playAct.setEnabled(False)
            self.stopAct.setEnabled(False)
            self.camPropDock.close()
            self.toggleCamPropAct.setChecked(False)
            self.toggleCamPropAct.setEnabled(False)

    @pyqtSlot()
    def startStreaming(self):
        if (self.camD.state == PGCameraStates.Streaming):
            return

        config = self.cameraConfigWidget.cam_config
        format = QVideoSurfaceFormat(QSize(config['cam_w'], config['cam_h']), QVideoFrame.Format_RGB24)

        self.camView.surface.stop()
        self.camView.surface.start(format)

        self.camD.stream(True)

    @pyqtSlot()
    def stopStreaming(self):
        self.camD.stream(False)

    @pyqtSlot()
    def restartCamStream(self, triggered=True):
        self.stopStreaming()
        time.sleep(0.2)
        self.cameraConfigWidget.updateConfig(True)
        config = self.cameraConfigWidget.cam_config
        self.changeCameraConfig(config)
        # # self.cameraInfo.updateCamConfig(config)
        # time.sleep(0.1)
        QTimer.singleShot(self.camView.RESTART_TIME, self.startStreaming)

    @pyqtSlot()
    def updateViewToolTip(self, *args, **kwargs):
        self.camView.setToolTip(self.cameraInfo.getRichText())

    @pyqtSlot(PGCameraStates, PGCameraStates)
    def updateCamStatus(self, newState, oldState):
        self.camStatusLbl.setText("<b>Status</b>:    " + newState.name)
        self.camStatusIcon.setText("<img src=\"" + self.statusIcons[newState.name] + "\">")

        if (self.camD.state == PGCameraStates.Streaming):
            self.playAct.setEnabled(False)
            self.stopAct.setEnabled(True)
            self.toggleCamPropAct.setEnabled(True)
            if (not self.camPropWidget.initialized):
                self.camPropWidget.setupUI(self.camD)
        elif self.camD.state == PGCameraStates.Connected:
            self.playAct.setEnabled(True)
            self.stopAct.setEnabled(False)
            self.toggleCamPropAct.setEnabled(True)
            if (not self.camPropWidget.initialized):
                self.camPropWidget.setupUI(self.camD)
        else:
            self.playAct.setEnabled(False)
            self.stopAct.setEnabled(False)
            self.camPropDock.close()
            self.toggleCamPropAct.setChecked(False)
            self.toggleCamPropAct.setEnabled(False)

    @pyqtSlot(dict)
    def changeCameraConfig(self, config):
        """

        :param config: dictionary containing configuration values
        :return:
        """
        self.cameraInfo.updateCamConfig(config)
        self.camD.changeCameraConfig(**config)
        self.camView.setToolTip(self.cameraInfo.getRichText())
        fr = self.camD.getFrameRate()

        # -1 indicates error
        if fr == -1 or fr is None:
            return
        else:
            self.camView.FRAME_RATE = fr