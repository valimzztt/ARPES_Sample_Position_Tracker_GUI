import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIntValidator
import flycapture2 as fc2
from utilities import ErrorPriority


class CameraConfigureWidget(QWidget):
    """
    This class holds settings for the PG Camera
    """
    cameraConfigChanged = pyqtSignal(dict)
    erroredOut = pyqtSignal(str, ErrorPriority)
    usedCamIndices = []

    def __init__(self, parent=0):
        QWidget.__init__(self, parent)
        self.camContext = fc2.Context()

        cam_config = dict()
        cam_config['cam_index'] = 0
        cam_config['cam_mode'] = 0
        cam_config['cam_x'] = 0
        cam_config['cam_y'] = 0
        cam_config['cam_w'] = 1280
        cam_config['cam_h'] = 960

        # guarantees an unused addStr
        while cam_config['cam_index'] in CameraConfigureWidget.usedCamIndices:
            cam_config['cam_index'] += 1
            if cam_config['cam_index'] >= self.camContext.get_num_of_cameras() or cam_config['cam_index'] < 0:
                self.erroredOut.emit('No valid camera indices left!', ErrorPriority.Critical)

        self.cam_config = cam_config

        self.setupUI()
        self.reloadConfigData()

    def __del__(self):
        if(self.cam_config['cam_index'] in CameraConfigureWidget.usedCamIndices):
            CameraConfigureWidget.usedCamIndices.remove(self.cam_config['cam_index'])

    def setupUI(self):
        camConfigGB = QGroupBox('Camera Configuration')

        camIndexLbl = QLabel('Camera Index:')
        self.camIndexCombo = QComboBox()
        self.camIndexCombo.addItems([str(i) for i in range(self.camContext.get_num_of_cameras())])
        self.camIndexCombo.setToolTip("Index of camera to use")

        camModeLbl = QLabel('Camera Mode:')
        self.camModeCombo = QComboBox()
        self.camModeCombo.addItems([str(i) for i in [0, 1, 2, 4, 7, 8, 10]]) # Video Modes
        self.camModeCombo.setToolTip("Format 7 Camera mode to use")


        hbox = QHBoxLayout()
        hbox.addWidget(camIndexLbl)
        hbox.addWidget(self.camIndexCombo)
        hbox.addWidget(camModeLbl)
        hbox.addWidget(self.camModeCombo)

        camConfigGB.setLayout(hbox)

        camVFGB = QGroupBox('Viewport')

        camX_lbl = QLabel("X Offset:")
        self.camX_edit = QLineEdit()
        self.camX_edit.setValidator(QIntValidator())
        self.camX_edit.setToolTip("X-Offset for ROI")

        camY_lbl = QLabel("Y Offset:")
        self.camY_edit = QLineEdit()
        self.camY_edit.setValidator(QIntValidator())
        self.camY_edit.setToolTip("Y-Offset for ROI")

        camW_lbl = QLabel("Width:")
        self.camW_edit = QLineEdit()
        self.camW_edit.setValidator(QIntValidator())
        self.camW_edit.setToolTip("Width of ROI")

        camH_lbl = QLabel("Height:")
        self.camH_edit = QLineEdit()
        self.camH_edit.setValidator(QIntValidator())
        self.camH_edit.setToolTip("Height of ROI")

        viewGrid = QGridLayout()
        viewGrid.addWidget(camX_lbl, 0, 0)
        viewGrid.addWidget(self.camX_edit, 0, 1)
        viewGrid.addWidget(camY_lbl, 0, 2)
        viewGrid.addWidget(self.camY_edit, 0, 3)
        viewGrid.addWidget(camW_lbl, 1, 0)
        viewGrid.addWidget(self.camW_edit, 1, 1)
        viewGrid.addWidget(camH_lbl, 1, 2)
        viewGrid.addWidget(self.camH_edit, 1, 3)

        camVFGB.setLayout(viewGrid)

        resetBtn = QPushButton("Reload Data")
        resetBtn.clicked.connect(self.reloadConfigData)
        resetBtn.setToolTip("Re-checks camera settings, and loads the current camera configuration")
        configBtn = QPushButton("Configure Camera")
        configBtn.clicked.connect(self.emitConfigChange)
        configBtn.setToolTip("Updates the camera with the given settings")

        mainGrid = QGridLayout(self)
        mainGrid.addWidget(camConfigGB, 0, 0, 1, 2)
        mainGrid.addWidget(camVFGB, 1, 0, 1, 2)
        mainGrid.addWidget(resetBtn, 2, 0, 1, 1)
        mainGrid.addWidget(configBtn, 2, 1, 1, 1)


        self.setLayout(mainGrid)


    def reloadConfigData(self):
        """
        Loads the config from the class' cam_config variable into each field
        :return:
        """
        self.camIndexCombo.clear()
        self.camIndexCombo.addItems([str(i) for i in range(self.camContext.get_num_of_cameras())])

        self.camIndexCombo.setCurrentIndex(int(self.cam_config['cam_index']))
        self.camModeCombo.setCurrentText(str(self.cam_config['cam_mode']))
        self.camX_edit.setText(str(self.cam_config['cam_x']))
        self.camY_edit.setText(str(self.cam_config['cam_y']))
        self.camW_edit.setText(str(self.cam_config['cam_w']))
        self.camH_edit.setText(str(self.cam_config['cam_h']))



    def emitConfigChange(self):
        self.updateConfig(True)

        self.cameraConfigChanged.emit(self.cam_config)

    def updateConfig(self, verbose=False):
        self.cam_config['cam_index'] = self.camIndexCombo.currentIndex()
        error_msgs = []
        txt = self.camModeCombo.currentText()
        if (txt != ''):
            self.cam_config['cam_mode'] = int(txt)
        else:
            error_msgs.append("Camera Mode {0} is invalid!".format(txt))
        txt = self.camX_edit.text()
        if (txt != ''):
            self.cam_config['cam_x'] = int(txt)
        else:
            error_msgs.append("X Offset must be a valid integer!")
        txt = self.camY_edit.text()
        if (txt != ''):
            self.cam_config['cam_y'] = int(txt)
        else:
            error_msgs.append("Y Offset must be a valid integer!")
        txt = self.camW_edit.text()
        if (txt != ''):
            self.cam_config['cam_w'] = int(txt)
        else:
            error_msgs.append("View-port Width must be a valid integer!")
        txt = self.camH_edit.text()
        if (txt != ''):
            self.cam_config['cam_h'] = int(txt)
        else:
            error_msgs.append("View-port Height must be a valid integer!")
        if (len(error_msgs) > 0):

            self.erroredOut.emit(
                "Camera Configuration Error: " + '\n'.join(error_msgs) + ' Configuration of these parameters skipped.',
                ErrorPriority.Critical)
            return False
        else:
            return True
