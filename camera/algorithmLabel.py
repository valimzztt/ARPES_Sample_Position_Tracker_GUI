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

        displayText += "<b>Mean X:</b>" + str(sum(self.x)/len(self.x)) + "\n"
        displayText += "<b>Mean Y:</b>" + str(sum(self.y)/len(self.y)) + "\n"

        self.text.setText(displayText)