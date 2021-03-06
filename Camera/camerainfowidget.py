from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMainWindow,  QProgressBar,  QTableWidgetItem)
from PyQt5.Qt import QThread, QThreadPool, QRunnable, QObject, QWidget, QApplication, QPushButton, QGridLayout, QTextEdit, pyqtSignal, QTextCursor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from IDS_Camera import CameraDaemon


import time
import threading
from qtpy import QtWidgets
import qt_thread_updater
# from qt_thread_updater import get_updater




class CameraInfoWidget(QWidget):


    """
    Widget that displays Camera information
    """

    def __init__(self, parent=0):
        QWidget.__init__(self, parent)
        self.setupUI()


    def setupUI(self):
        self.setupCamInfo()
        self.setupCamConfig()

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.camInfoGB)
        self.mainLayout.addWidget(self.camConfigGB)

        self.setLayout(self.mainLayout)

    def setupCamInfo(self):
        global camera_info
        camera_info = CameraDaemon.get_camera_info()
        camera_model = camera_info['Camera model']
        serial_number = camera_info['Serial number']


        self.info = {camera_model : QLabel(),
                         "firmware_version" :QLabel(),
                         "sensor_info" : QLabel(),
                         "sensor_resolution" :QLabel(),
                         serial_number: QLabel(),
                         "Thorlabs Camera" :QLabel()}
        model_name = "Hello"

        print(self.info)


        for k, lbl in self.info.items():
            lbl.setAlignment(Qt.AlignRight)
            lbl.setText(k)


        info_vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()
        model = QLabel("Model: ")
        hbox.addWidget(model)
        hbox.addWidget(self.info[camera_model])
        info_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        firmware = QLabel("Firmware Version: ")
        hbox.addWidget(firmware)
        hbox.addWidget(self.info['firmware_version'])
        info_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        sensor_info = QLabel("Sensor Info: ")
        hbox.addWidget(sensor_info)
        hbox.addWidget(self.info['sensor_info'])
        info_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        sensor_res = QLabel("Sensor Resolution: ")
        hbox.addWidget(sensor_res)
        hbox.addWidget(self.info['sensor_resolution'])
        info_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        ser_num = QLabel("Serial #: ")
        hbox.addWidget(ser_num)
        hbox.addWidget(self.info[serial_number])
        info_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vendor = QLabel("Vendor: ")
        hbox.addWidget(vendor)
        hbox.addWidget(self.info['Thorlabs Camera'])
        info_vbox.addLayout(hbox)

        self.camInfoGB = QGroupBox('Camera Info')
        self.camInfoGB.setLayout(info_vbox)



    def setupCamConfig(self):
        self.config = dict(cam_index=QLabel(),
                           cam_mode=QLabel(),
                           cam_x=QLabel(),
                           cam_y=QLabel(),
                           cam_w=QLabel(),
                           cam_h=QLabel())

        for k, lbl in self.config.items():
            lbl.setAlignment(Qt.AlignRight)
            lbl.setText("---")

        status_vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()
        lbl = QLabel("Camera Index:")
        hbox.addWidget(lbl)
        hbox.addWidget(self.config['cam_index'])
        status_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        lbl = QLabel("Camera Mode:")
        hbox.addWidget(lbl)
        hbox.addWidget(self.config['cam_mode'])
        status_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        lbl = QLabel("X-Offset:")
        hbox.addWidget(lbl)
        hbox.addWidget(self.config['cam_x'])
        status_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        lbl = QLabel("Y-Offset:")
        hbox.addWidget(lbl)
        hbox.addWidget(self.config['cam_y'])
        status_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        lbl = QLabel("Width:")
        hbox.addWidget(lbl)
        hbox.addWidget(self.config['cam_w'])
        status_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        lbl = QLabel("Height:")
        hbox.addWidget(lbl)
        hbox.addWidget(self.config['cam_h'])
        status_vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        lbl = QLabel("Pixel Format:")
        hbox.addWidget(lbl)
        lbl = QLabel("24-bit RGB")
        lbl.setAlignment(Qt.AlignRight)
        hbox.addWidget(lbl)
        status_vbox.addLayout(hbox)

        self.camConfigGB = QGroupBox('Camera Settings')
        self.camConfigGB.setLayout(status_vbox)

    @pyqtSlot(dict)
    def updateCamInfo(self, info):
        camera_info = set_up_camera()
        for k, v in camera_info.items():
            if k in self.info:
                if(type(v) is bytes):
                    txt = v.decode()
                else:
                    txt = str(v)
                self.info[k].setText(txt)

    @pyqtSlot(dict)
    def updateCamConfig(self, config):
        for k, v in config.items():
            if k in self.config:
                if (type(v) is bytes):
                    txt = v.decode()
                else:
                    txt = str(v)
                self.config[k].setText(txt)

    def getRichText(self):
        """
        Produces a rich-text format output of Camera info and configuration values for use in a tooltip
        :return:
        """
        txt = "Model: " + self.info['model_name'].text() + '\n'
        txt += "Firmware Version: " + self.info['firmware_version'].text() + '\n'
        txt += "Sensor Info: " + self.info['sensor_info'].text() + '\n'
        txt += "Serial #: " + self.info['serial_number'].text() + '\n'
        txt += "Vendor: " + self.info['vendor_name'].text() + '\n'
        txt += "-----\n"
        txt += "Camera Index: " + self.config['cam_index'].text() + '\n'
        txt += "Camera Mode: " + self.config['cam_mode'].text() + '\n'
        txt += "X-Offset: " + self.config['cam_x'].text() + '\n'
        txt += "Y-Offset: " + self.config['cam_y'].text() + '\n'
        txt += "Resolution: " + self.config['cam_w'].text() + 'x' + self.config['cam_h'].text() + '\n'
        txt += "Pixel Format: " + "24-bit RGB"
        return txt



class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("test")
        self.setWindowIcon(QtGui.QIcon('clay.png'))

        # options inside file menu
        self.setCentralWidget

