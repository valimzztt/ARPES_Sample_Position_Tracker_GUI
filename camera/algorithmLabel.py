from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSlot

import numpy as np

class AlgorithmLabel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.text)

        self.hbox = QHBoxLayout()
        self.x1lbl = QLabel()
        self.x1lbl.setText('X1:')
        self.x1box = QDoubleSpinBox()
        self.hbox.addWidget(self.x1lbl)
        self.hbox.addWidget(self.x1box)

        self.x2lbl = QLabel()
        self.x2lbl.setText('X2:')
        self.x2box = QDoubleSpinBox()
        self.hbox.addWidget(self.x2lbl)
        self.hbox.addWidget(self.x2box)

        self.y1lbl = QLabel()
        self.y1lbl.setText('Y1:')
        self.y1box = QDoubleSpinBox()
        self.hbox.addWidget(self.y1lbl)
        self.hbox.addWidget(self.y1box)

        self.y2lbl = QLabel()
        self.y2lbl.setText('Y2:')
        self.y2box = QDoubleSpinBox()
        self.hbox.addWidget(self.y2lbl)
        self.hbox.addWidget(self.y2box)

        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)


        self.x = []
        self.y = []
        self.MEAN_LEN = 10


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
            self.y = self.y[1:]
            self.y.append(y)

        meanX = sum(self.x)/len(self.x)
        meanY = sum(self.y)/len(self.y)

        displayText += "<b>Mean X:</b>" + str(meanX) + "\n"
        displayText += "<b>Mean Y:</b>" + str(meanY) + "\n"

        Ypos = ((self.y2box.value()-self.y1box.value())/(self.x2box.value()-self.x1box.value()))*(meanX-self.x1box.value()) + self.y1box.value()

        displayText += "<b>Y-Pos:</b>" + str(Ypos)


        self.text.setText(displayText)