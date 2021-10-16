import sys
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIntValidator
import sys
import os
from IDS_Camera import CameraDaemon
import time
import threading
from qtpy import QtWidgets
import qt_thread_updater
# from qt_thread_updater import get_updater



class CameraConfigureWidget(QWidget):
    """
    This class holds settings for the PG Camera
    """
    cameraConfigChanged = pyqtSignal(dict)
    usedCamIndices = []

    def __init__(self, parent=0):
        QWidget.__init__(self, parent)

        cam_config = dict()
        cam_config['cam_index'] = 0
        cam_config['cam_mode'] = 0
        cam_config['cam_x'] = 0
        cam_config['cam_y'] = 0
        cam_config['cam_w'] = 1280
        cam_config['cam_h'] = 960
        self.camera_info = CameraDaemon.set_up_camera()

        # guarantees an unused addStr
        while cam_config['cam_index'] in CameraConfigureWidget.usedCamIndices:
            cam_config['cam_index'] += 1

        self.cam_config = cam_config

        self.setupUI()

    def __del__(self):
        if(self.cam_config['cam_index'] in CameraConfigureWidget.usedCamIndices):
            CameraConfigureWidget.usedCamIndices.remove(self.cam_config['cam_index'])

    def setupUI(self):
        global counter

        camVFGB = QGroupBox('Viewport')

        camX_lbl = QLabel("X Offset:")
        self.camX_edit = QLineEdit()
        self.camX_edit.setValidator(QIntValidator())
        self.camX_edit.setToolTip("X-Offset for ROI")




        def run(is_alive):
            global counter

            is_alive.set()
            while is_alive.is_set():
                counter = list(CameraDaemon.counter_runner())
                #data['counter'] += 1
                # time.sleep(0.001)  # Not needed (still good to have some delay to release the thread)

        alive = threading.Event()
        th = threading.Thread(target=run, args=(alive,))
        th.start()


        # get_updater().register_continuous(update)



        camY_lbl = QLabel("Y Offset:")
        self.camY_edit = QLineEdit()
        self.camY_edit.setValidator(QIntValidator())
        self.camY_edit.setToolTip("Y-Offset for ROI")

        camW_lbl = QLabel("Width:")
        self.camW_edit = QLineEdit(self)
        self.camW_edit.setText(str(self.camera_info))
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


        mainGrid = QGridLayout(self)
        mainGrid.addWidget(camVFGB, 1, 0, 1, 2)


        self.setLayout(mainGrid)





