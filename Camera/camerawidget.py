import time

from PyQt5.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtMultimedia import QVideoSurfaceFormat, QVideoFrame
from PyQt5.QtWidgets import *
from Camera.cameraconfigwidget import *
from Camera.camerainfowidget import CameraInfoWidget
from Camera.algorithmLabel import *
from Camera.camerapropwidget import CameraPropertiesWidget
from Camera.viewfinderwidget import ViewfinderWidget
from algorithmchoice import WidgetGallery2, Worker
import IDS_Camera


class CameraWidget(QWidget):
    camlist = [] # list of Camera widgets
    addCameraRequested = pyqtSignal(str)
    removeCameraRequested = pyqtSignal()

    def __init__(self, parent=None, name=''):
        super().__init__(parent)
        CameraWidget.camlist.append(self)

        if parent:
            self.main = parent # first parent is always the mainwindow
        else:
            return

        camNum = len(CameraWidget.camlist)
        if camNum > 1:
            if name == '':
                self.name = '#'+ str(camNum)
            else:
                self.name = name

            self.addStr = " ({0})".format(self.name)
        else:
            self.name = ''
            self.addStr = ''

        self.setObjectName('Camera View' + self.addStr)

        self.setupUI()
        self.setupView()
        #self.setupCamDaemon()


    def setupUI(self):
        self.cameraConfigWidget = CameraConfigureWidget(self)
        self.camConfigDock = QDockWidget("Camera Configuration" + self.addStr, self)
        self.camConfigDock.setWidget(self.cameraConfigWidget)
        self.camConfigDock.setObjectName("Camera Configuration" + self.addStr)
        self.main.addDockWidget(Qt.BottomDockWidgetArea, self.camConfigDock)

        self.cameraInfo = CameraInfoWidget(self)
        self.camInfoDock = QDockWidget("Camera Info" + self.addStr, self)
        self.camInfoDock.setWidget(self.cameraInfo)
        self.camInfoDock.setObjectName("Camera Info" + self.addStr)
        self.main.addDockWidget(Qt.BottomDockWidgetArea, self.camInfoDock)

        self.algoLabel = AlgorithmLabel(self)
        self.algoDock = QDockWidget("Algorithm Data" + self.addStr, self)
        self.algoDock.setWidget(self.algoLabel)
        self.algoDock.setObjectName("Algorithm Data" + self.addStr)
        self.main.addDockWidget(Qt.RightDockWidgetArea, self.algoDock)

        self.algoChoice = WidgetGallery2(self)
        self.algoChoiceDock = QDockWidget("Algorithm Choice" + self.addStr, self)
        self.algoChoiceDock.setWidget(self.algoChoice)
        self.algoChoiceDock.setObjectName("Algortihm Choice" + self.addStr)
        self.main.addDockWidget(Qt.RightDockWidgetArea, self.algoChoiceDock)

        self.cameraConfigWidget.cameraConfigChanged.connect(self.changeCameraConfig)


    def setupView(self):
        self.camView = ViewfinderWidget(self)

        camNum = len(CameraWidget.camlist)
        if camNum > 1:
            name = " #" + str(camNum - 1)
        else:
            name = ''

        self.setupCameraToolbar(name)

        vbox = QVBoxLayout()
        vbox.addWidget(self.toolBar)
        vbox.addWidget(self.camView)


        self.setLayout(vbox)


    def setupCameraToolbar(self, name):
        self.toolBar = QToolBar('Camera' + name)
        lbl = QLabel("<b>Camera Controls</b>:")
        self.toolBar.addWidget(lbl)
        playIcon = QIcon('resources/button_blue_play.png')
        self.playAct = QAction(playIcon, "Play", self)
        self.playAct.setToolTip("Start Camera strean")
        stopIcon = QIcon('resources/button_blue_stop.png')
        self.stopAct = QAction(stopIcon, "Stop", self)
        self.stopAct.setToolTip("Stop Camera stream")
        self.toolBar.addAction(self.playAct)
        self.toolBar.addAction(self.stopAct)

        #camPropIcon = QIcon('resources/aperture.png')
        #self.toggleCamPropAct = self.camPropDock.toggleViewAction()
        #self.toggleCamPropAct.setIcon(camPropIcon)
        #self.toggleCamPropAct.setToolTip("Show/Hide Camera Properties")
        #self.toolBar.addAction(self.toggleCamPropAct)
        #self.toolBar.addSeparator()

        self.toolBar.setObjectName("Camera Controls" + name)
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
        self.restartCamAct.setToolTip("Re-configure and restart Camera stream")
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
        self.toolBar.addSeparator()

        camSaveIcon = QIcon('resources/save.png')
        self.camSaveAct = QAction(camSaveIcon, "Save Image", self)
        self.camSaveAct.setToolTip("Save current frame")
        self.toolBar.addAction(self.camSaveAct)
        self.playAct.triggered.connect(self.startStreaming)
        self.stopAct.triggered.connect(self.stopStreaming)
        self.restartCamAct.triggered.connect(self.restartCamStream)
        self.camSaveAct.triggered.connect(self.camView.saveCurrentFrame)
        self.toolBar.addSeparator()

        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolBar.addWidget(empty)
        lbl = QLabel("<b>Camera Views:</b>")
        self.toolBar.addWidget(lbl)
        camAddIcon = QIcon('resources/camera_new.png')



    @pyqtSlot(dict)
    def changeCameraConfig(self, config):
        """

        :param config: dictionary containing configuration values
        :return:
        """
        self.camPropWidget.cam_mode = config['cam_mode']
        self.camPropWidget.updateShutterLims()
        self.cameraInfo.updateCamConfig(config)
        self.camD.changeCameraConfig(**config)
        self.camView.setToolTip(self.cameraInfo.getRichText())
        fr = self.camD.getFrameRate()

        # -1 indicates error
        if fr == -1 or fr is None:
            return
        else:
            self.camView.FRAME_RATE = fr



    @pyqtSlot()
    def startStreaming(self):
        if (self.camD.state == PGCameraStates.Streaming):
            return

        config = self.cameraConfigWidget.cam_config
        format = QVideoSurfaceFormat(QSize(int(config['cam_w']), int(config['cam_h'])), QVideoFrame.Format_RGB24)

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

    @pyqtSlot(bool)
    def selectSample(self, checked):
        if checked:
            cursor = QCursor()
            cursor.setShape(Qt.PointingHandCursor)
            self.camView.setCursor(cursor)
        else:
            cursor = QCursor()
            cursor.setShape(Qt.ArrowCursor)
            self.camView.setCursor(cursor)