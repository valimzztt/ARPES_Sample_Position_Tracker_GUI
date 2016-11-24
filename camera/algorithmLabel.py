from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from utilities import ErrorPriority
import numpy as np

class AlgorithmLabel(QWidget):
    erroredOut = pyqtSignal(str, ErrorPriority)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.text)

        self.hbox = QHBoxLayout()
        self.x1lbl = QLabel()
        self.x1lbl.setText('x1:')
        self.x1box = QDoubleSpinBox()
        self.x1box.setRange(1, 1000)
        self.hbox.addWidget(self.x1lbl)
        self.hbox.addWidget(self.x1box)

        self.x2lbl = QLabel()
        self.x2lbl.setText('x2:')
        self.x2box = QDoubleSpinBox()
        self.x2box.setRange(1, 1000)
        self.hbox.addWidget(self.x2lbl)
        self.hbox.addWidget(self.x2box)

        self.Y1lbl = QLabel()
        self.Y1lbl.setText('Y1:')
        self.Y1box = QDoubleSpinBox()
        self.Y1box.setRange(1, 1000)
        self.hbox.addWidget(self.Y1lbl)
        self.hbox.addWidget(self.Y1box)

        self.Y2lbl = QLabel()
        self.Y2lbl.setText('Y2:')
        self.Y2box = QDoubleSpinBox()
        self.Y2box.setRange(1, 1000)
        self.hbox.addWidget(self.Y2lbl)
        self.hbox.addWidget(self.Y2box)

        self.vbox.addLayout(self.hbox)

        self.hbox = QHBoxLayout()
        self.y1lbl = QLabel()
        self.y1lbl.setText('y1:')
        self.y1box = QDoubleSpinBox()
        self.y1box.setRange(1, 1000)
        self.hbox.addWidget(self.y1lbl)
        self.hbox.addWidget(self.y1box)

        self.y2lbl = QLabel()
        self.y2lbl.setText('y2:')
        self.y2box = QDoubleSpinBox()
        self.y2box.setRange(1, 1000)
        self.hbox.addWidget(self.y2lbl)
        self.hbox.addWidget(self.y2box)

        self.Z1lbl = QLabel()
        self.Z1lbl.setText('Z1:')
        self.Z1box = QDoubleSpinBox()
        self.Z1box.setRange(1, 1000)
        self.hbox.addWidget(self.Z1lbl)
        self.hbox.addWidget(self.Z1box)

        self.Z2lbl = QLabel()
        self.Z2lbl.setText('Z2:')
        self.Z2box = QDoubleSpinBox()
        self.Z2box.setRange(1, 1000)
        self.hbox.addWidget(self.Z2lbl)
        self.hbox.addWidget(self.Z2box)

        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)


        self.x = []
        self.y = []
        self.MEAN_LEN = 5


    @pyqtSlot(int, int ,int ,int, int)
    def displayData(self, x, y, w, h, area):
        displayText = ""

        displayText += "<b>X:</b>" + str(x) + "\n"
        displayText += "<b>Y:</b>" + str(y) + "\n"
        displayText += "<b>W:</b>" + str(w) + "\n"
        displayText += "<b>H:</b>" + str(h) + "\n"
        displayText += "<b>Area:</b>" + str(area) + "\n"

        if len(self.x) < self.MEAN_LEN:
            self.x.append(x)
        else:
            self.x = self.x[1:]
            self.x.append(x)

        if len(self.y) < self.MEAN_LEN:
            self.y.append(x)
        else:
            self.y.pop(0)
            self.y.append(y)

        meanX = sum(self.x)/len(self.x)
        meanY = sum(self.y)/len(self.y)

        displayText += "<b>Mean X:</b>" + str(meanX) + "\n"
        displayText += "<b>Mean Y:</b>" + str(meanY) + "\n"

        try:
            Ypos = ((self.Y2box.value() - self.Y1box.value()) / (self.x2box.value() - self.x1box.value())) * (meanX - self.x1box.value()) + self.Y1box.value()

            displayText += "<b>Y-Pos:</b>" + str(Ypos) + "\n"

            Zpos = ((self.Z2box.value() - self.Z1box.value()) / (self.y2box.value() - self.y1box.value())) * (meanY - self.y1box.value()) + self.Z1box.value()

            displayText += "<b>Z-Pos:</b>" + str(Zpos) + "\n"
        except ZeroDivisionError as e:
            self.erroredOut.emit("Invalid calibration coordinates. Please check calibration coordinates. x, y corresponds to pixels, Y, Z corresponds to real dimensions.", ErrorPriority.Warning)


        self.text.setText(displayText)