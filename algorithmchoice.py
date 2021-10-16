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
from Camera.cameraconfigwidget import CameraConfigureWidget

from IDS_Camera import CameraDaemon
import sys
import IDS_Camera
import time



class Stream(QtCore.QObject):
    """Redirects console output to text widget."""
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, monitor_time, magnification_factor):
        super(Worker, self).__init__()
        self.monitor_time = monitor_time
        self.magnification_factor = magnification_factor
        self.algorithm_choice = algorithm_chosen


    def run(self):
        """Long-running task."""
        for i in range(monitor_time):
            print("helllo, magnifiaction factor is" + str(magnification_factor))
            #time.sleep(1)
            #self.progress.emit(i + 1)
        #self.finished.emit()

    def open_camera(self):
        print("Open CAMERA")
        #pixel_recording(monitor_time, "Algorithm1")
        CameraDaemon.retrieve_offset(monitor_time, algorithm_chosen)

    def setting_up_camera(self):
        CameraDaemon.hello(self)
        #CameraConfigureWidget.change_width(self)
        #CameraDaemon.set_up_camera(self)
        #CameraConfigureWidget.change_width(self)


class WidgetGallery2(QDialog):
    global algorithm_chosen
    #Default algorithm is 1
    algorithm_chosen = "Algorithm 1"
    global monitor_time
    monitor_time = 20
    global magnification_factor
    magnification_factor = 30


    def __init__(self, parent=None):
        super().__init__(parent)
        # Note that this sentence can be printed to the console for easy debugging
        sys.stdout = Stream(newText=self.onUpdateCameraInfo)

        self.clicksCount = 0
        self.monitor_time = monitor_time
        self.magnification_factor = magnification_factor
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()

        topLayout = QHBoxLayout()
        topLayout.addStretch(1)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Styles")
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def onUpdateCameraInfo(self, text):
        """Write console output to text widget."""
        cursor = self.processCam.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.processCam.setTextCursor(cursor)
        self.processCam.ensureCursorVisible()

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)


    def reportProgress(self, n):
        self.stepLabel.setText(f"Long-Running Step: {n}")

    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(self.monitor_time, self.magnification_factor)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.open_camera)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.longRunningBtn.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.longRunningBtn.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.stepLabel.setText("Long-Running Step: 0")
        )
    def runLongTask2(self):
        # Step 2: Create a QThread object
        self.thread2 = QThread()
        # Step 3: Create a worker object
        self.worker2 = Worker(self.monitor_time, self.magnification_factor)
        # Step 4: Move worker to the thread
        self.worker2.moveToThread(self.thread2)
        # Step 5: Connect signals and slots
        self.thread2.started.connect(self.worker2.setting_up_camera)
        self.worker2.finished.connect(self.thread2.quit)
        self.worker2.finished.connect(self.worker2.deleteLater)
        self.thread2.finished.connect(self.thread2.deleteLater)
        # Step 6: Start the thread
        self.thread2.start()

        # Final resets
        self.longRunningBtn2.setEnabled(False)
        self.thread2.finished.connect(
            lambda: self.longRunningBtn2.setEnabled(True)
        )
        self.thread2.finished.connect(
            lambda: self.stepLabel.setText("Long-Running Step: 0")
        )




    def alg1(self):
        global algorithm_chosen
        print(self.radioButton1.text() + " will be used to calculate the pixel shift")

        algorithm_chosen = "Algorithm 1"
    def alg2(self):
        global algorithm_chosen
        print(self.radioButton2.text() + " will be used to calculate the pixel shift")
        algorithm_chosen = "Algorithm 2"
    def alg3(self):
        global algorithm_chosen
        print(self.radioButton3.text() + " will be used to calculate the pixel shift")
        algorithm_chosen = "Algorithm 3"
    def alg4(self):
        global algorithm_chosen
        print(self.radioButton4.text() + " will be used to calculate the pixel shift")
        algorithm_chosen = "Algorithm 4"
    def alg5(self):
        global algorithm_chosen
        print(self.radioButton5.text() + " will be used to calculate the pixel shift")
        algorithm_chosen = "Algorithm 5"

    def createTopLeftGroupBox(self):

        self.topLeftGroupBox = QGroupBox("Group 1")
        self.topLeftGroupBox = QGroupBox("Algorithms choice")

        # Create and connect widgets
        #self.stepLabel = QLabel("Long-Running Step: 0")
        #self.stepLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


        self.radioButton1 = QRadioButton("Algorithm 1")
        self.radioButton2 = QRadioButton("Algorithm 2")
        self.radioButton3 = QRadioButton("Algorithm 3")
        self.radioButton4 = QRadioButton("Algorithm 4")
        self.radioButton5 = QRadioButton("Algorithms combined")

        self.radioButton1.pressed.connect(self.alg1)
        self.radioButton2.pressed.connect(self.alg2)
        self.radioButton3.pressed.connect(self.alg3)
        self.radioButton4.pressed.connect(self.alg4)
        self.radioButton5.pressed.connect(self.alg5)

        layout = QVBoxLayout()
        #layout.addWidget(self.stepLabel)
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.radioButton2)
        layout.addWidget(self.radioButton3)
        layout.addWidget(self.radioButton4)
        layout.addWidget(self.radioButton5)
        self.topLeftGroupBox.setLayout(layout)


    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Offset monitoring")

        #CameraButton = QPushButton("Open Camera")
        self.SetUpCameraButton = QPushButton("Retrieve Camera Information")


        # connecting second button to the camera open streaming
        self.longRunningBtn2 = QPushButton("Set up Camera, press before starting to monitor", self)
        self.longRunningBtn2.clicked.connect(self.runLongTask2)

        # connecting first long running button to pixel offset
        self.longRunningBtn = QPushButton("Long-Running Task!", self)
        self.longRunningBtn.clicked.connect(self.runLongTask)

        btn_start = QPushButton("Start monitoring")
        btn_stop = QPushButton("Stop")
        btn_pause = QPushButton("Pause")
        btn_resume = QPushButton("Resume")

        layout = QVBoxLayout()
        #layout.addWidget(CameraButton)
        layout.addWidget(self.longRunningBtn2)
        layout.addWidget(self.longRunningBtn)
        layout.addWidget(self.SetUpCameraButton)
        layout.addWidget(btn_start)
        layout.addWidget(btn_stop)
        layout.addWidget(btn_pause)
        layout.addWidget(btn_resume)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

        # Create the text output widget.
        self.processCam = QTextEdit(self, readOnly=True)
        self.processCam.ensureCursorVisible()
        self.processCam.setLineWrapColumnOrWidth(500)
        self.processCam.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.processCam.setFixedWidth(400)
        self.processCam.setFixedHeight(150)
        self.processCam.move(30, 100)

        layout.addWidget(self.processCam)
        self.topRightGroupBox.setLayout(layout)


    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        self.tab1 = QWidget()
        self.tableWidget = QTableWidget(10, 3)
        self.tableWidget.setHorizontalHeaderLabels(['Image Index', 'X pixel offset', 'Y pixel offset'])

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(self.tableWidget)
        self.tab1.setLayout(tab1hbox)

        # When stop_btn is clicked this runs. Terminates the worker and the thread.

        self.bottomLeftTabWidget.addTab(self.tab1, "&Table")


    #CHANGING MONITOR TIME AND MAGNIFICATION FACTOR
    def change_monitoring_time(self):
        global monitor_time
        monitor_time, okPressed = QInputDialog.getInt(self, "Set monitoring time","Monitoring time (in seconds):", 10, 0, 10000, 1)
        if okPressed:
            self.monitorLabel.setText("Current monitoring time is: " + str(monitor_time))
            #self.change_monitor_time(monitor_time)

    def change_magnification_factor(self):
        global magnification_factor
        magnification_factor, okPressed = QInputDialog.getInt(self, "Set magnification factor","Magnification factor:", 20, 0, 10000, 1)
        if okPressed:
            self.magnificationLabel.setText("Current magnification factor is: " + str(magnification_factor))
            #self.change_magnification_factor(magnification_factor)



    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Group 3")
        layout = QVBoxLayout()
        self.btn1 = QPushButton("Select magnification factor")
        self.btn1.clicked.connect(self.change_magnification_factor)
        self.btn2 = QPushButton("Select monitoring time")
        self.btn2.clicked.connect(self.change_monitoring_time)

        #displaying current magnification and monitoring time
        self.magnificationLabel = QLabel("Current magnification factor is: " + str(self.magnification_factor))
        # self.stepLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)self.stepLabel = QLabel("Long-Running Step: 0")
        #         #self.stepLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.monitorLabel = QLabel("Current monitoring time is:" + str(self.monitor_time))

        layout.addWidget(self.btn2)
        layout.addWidget(self.monitorLabel)
        layout.addWidget(self.btn1)
        layout.addWidget(self.magnificationLabel)


        layout.addStretch(1)
        self.bottomRightGroupBox.setLayout(layout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gallery = WidgetGallery2()
    gallery.show()
    sys.exit(app.exec_())
