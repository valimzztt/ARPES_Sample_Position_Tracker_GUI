from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from enum import Enum, unique

@unique
class ErrorHandlingModes(Enum):
    Default = 0
    Verbose = 1
    Quiet = 2
    Disabled = 3


class SettingsDialog(QDialog):
    def __init__(self, errorMode=ErrorHandlingModes.Default.value, saveGeometryOnClose=True, saveCameraPropertiesOnClose=True, saveConfigOnClose=True, parent=0):
        QDialog.__init__(self, parent)

        mainLayout = QVBoxLayout()

        errorGB = QGroupBox('Error Handling')
        errorVBox = QVBoxLayout()
        self.errorCombo = QComboBox()
        self.errorCombo.addItems([k for k, v in ErrorHandlingModes.__members__.items()])
        self.errorCombo.setCurrentIndex(errorMode)
        self.errorCombo.setToolTip("<b>Default:</b> only critical errors are shown in a dialog box, everything else is printed\n"
                                   "<b>Verbose:</b> all errors are shown as a dialog box and printed\n"
                                   "<b>Quiet:</b> no dialog box is shown for any error, it is printed instead\n"
                                   "<b>Disabled:</b> errors are completely ignored")
        errorVBox.addWidget(self.errorCombo)
        errorGB.setLayout(errorVBox)
        mainLayout.addWidget(errorGB)

        saveloadGB = QGroupBox('Saving/Loading')
        saveloadVBox = QVBoxLayout()
        self.saveGeoCheck = QCheckBox('Save/Load Window Geometry on Close/Startup.')
        self.saveGeoCheck.setChecked(saveGeometryOnClose)
        self.savePropsCheck = QCheckBox('Save/Load Camera Properties on Close/Startup.')
        self.savePropsCheck.setChecked(saveCameraPropertiesOnClose)
        self.saveConfigCheck = QCheckBox('Save/Load Camera Configuration on Close/Startup.')
        self.saveConfigCheck.setChecked(saveConfigOnClose)
        saveloadVBox.addWidget(self.saveGeoCheck)
        saveloadVBox.addWidget(self.savePropsCheck)
        saveloadVBox.addWidget(self.saveConfigCheck)
        saveloadGB.setLayout(saveloadVBox)
        mainLayout.addWidget(saveloadGB)

        hbox = QHBoxLayout()

        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        hbox.addWidget(ok)
        hbox.addWidget(cancel)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)
        self.setModal(True)






