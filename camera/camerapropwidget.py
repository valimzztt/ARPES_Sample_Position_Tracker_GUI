import copy
from enum import Enum, unique

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import *


@unique
class PGCameraProperties(Enum):
    BRIGHTNESS = 0
    AUTO_EXPOSURE = 1
    SHARPNESS = 2
    WHITE_BALANCE = 3
    HUE = 4
    SATURATION = 5
    GAMMA = 6
    IRIS = 7
    FOCUS = 8
    ZOOM = 9
    PAN = 10
    TILT = 11
    SHUTTER = 12
    GAIN = 13
    TRIGGER_MODE = 14
    TRIGGER_DELAY = 15
    FRAME_RATE = 16
    TEMPERATURE = 17


class CameraPropertiesWidget(QWidget):
    """
    Widget to adjust camera properties
    """
    propertyChanged = pyqtSignal(str)

    def __init__(self, parent=0):
        QWidget.__init__(self, parent=parent)
        self.properties = dict()
        self.savedProperties = dict()
        self.initialized = False

    def setupUI(self, camD, config):
        self.camD = camD
        self.update_properties()
        self.cam_mode = config['cam_mode']

        self.mainLayout = QVBoxLayout(self)

        self.labels = dict()
        self.sliders = dict()
        self.spinboxes = dict()
        self.autoBoxes = dict()
        self.enableBoxes = dict()

        labelLayout = QVBoxLayout()
        grid_sliders = QGridLayout()
        grid_checkboxes = QGridLayout()

        # vertSpacing = 0
        # # labelLayout.setSpacing(vertSpacing)
        # labelLayout.setContentsMargins(3, 3, 0, 3)
        # # grid_sliders.setVerticalSpacing(vertSpacing)
        # grid_sliders.setContentsMargins(0, 3, 0, 3)
        # # grid_checkboxes.setVerticalSpacing(vertSpacing)
        # grid_checkboxes.setContentsMargins(0, 3, 0, 3)
        row = 0

        for propname in PGCameraProperties.__members__.keys():
            lbl = self.labels[propname] = QLabel("<b>"+ propname + ":</b>")
            labelLayout.addWidget(lbl)
            slider = self.sliders[propname] = QSlider(Qt.Horizontal, self)
            grid_sliders.addWidget(slider, row, 0)
            spin = self.spinboxes[propname] = QDoubleSpinBox(self)
            grid_sliders.addWidget(spin, row, 1)
            auto = self.autoBoxes[propname] = QCheckBox("Auto-adjust", self)
            grid_checkboxes.addWidget(auto, row, 0)
            enable = self.enableBoxes[propname] = QCheckBox("Enable", self)
            grid_checkboxes.addWidget(enable, row, 1)

            slider.setToolTip("Adjust the value of {0}".format(propname))
            spin.setToolTip("Adjust the value of {0}".format(propname))
            auto.setToolTip("Set whether the camera auto-adjusts this property")
            enable.setToolTip("Enable this property")

            slider.setObjectName(propname)
            spin.setObjectName(propname)
            auto.setObjectName(propname)
            enable.setObjectName(propname)

            slider.valueChanged.connect(self.updateProperty)
            spin.valueChanged.connect(self.updateProperty)
            auto.stateChanged.connect(self.setAutoAdjust)
            enable.stateChanged.connect(self.enableProperty)

            if(propname == PGCameraProperties.GAIN.name):
                slider.setRange(0, 24)
                spin.setRange(0, 24)
            elif(propname == PGCameraProperties.SHUTTER.name):
                slider.setRange(0.01, 32)
                spin.setRange(0.01, 32)
            elif(propname == PGCameraProperties.GAMMA.name):
                slider.setRange(0.5, 4)
                spin.setRange(0.5, 4)
                slider.setSingleStep(0.1)
                spin.setSingleStep(0.1)
            elif(propname == PGCameraProperties.FRAME_RATE.name):
                slider.setRange(1, 60)
                slider.setSingleStep(1)
                spin.setRange(1, 60)
                spin.setSingleStep(1)



            self.propertyChanged.connect(self.setProperty)

            row += 1



        grid_sliders.setColumnStretch(0, 0)
        grid_sliders.setColumnStretch(1, 0.5)
        grid_sliders.setColumnStretch(2, 0)

        # add widgets to a splitter for resize capabilities
        labelFrame = QFrame()
        labelFrame.setLayout(labelLayout)
        # labelFrame.setFrameShape(QFrame.Panel)
        # labelFrame.setFrameShadow(QFrame.Raised)
        sliderFrame = QFrame()
        sliderFrame.setLayout(grid_sliders)
        # sliderFrame.setFrameShape(QFrame.Panel)
        # sliderFrame.setFrameShadow(QFrame.Sunken)
        checkboxFrame = QFrame()
        checkboxFrame.setLayout(grid_checkboxes)
        # checkboxFrame.setFrameShape(QFrame.Panel)
        # checkboxFrame.setFrameShadow(QFrame.Sunken)
        splitter = QSplitter(self)
        splitter.addWidget(labelFrame)
        splitter.addWidget(sliderFrame)
        splitter.addWidget(checkboxFrame)
        splitter.setHandleWidth(10)
        splitter.setCollapsible(0, False) #labels aren't collapsible
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        # disable first splitter handle so labels can't be resized, add line to the splitter's handle
        handle = splitter.handle(1)
        handle.setEnabled(False)
        handleLayout = QVBoxLayout(handle)
        handleLayout.setSpacing(5)
        handleLayout.setContentsMargins(0,0,0,0)
        handleLine = QFrame(handle)
        handleLine.setFrameShape(QFrame.VLine)
        handleLine.setFrameShadow(QFrame.Sunken)
        handleLayout.addWidget(handleLine, 0, Qt.AlignHCenter)

        # add line to the splitter's handle
        handle = splitter.handle(2)
        handleLayout = QVBoxLayout(handle)
        handleLayout.setSpacing(5)
        handleLayout.setContentsMargins(0,0,0,0)
        handleLine = QFrame(handle)
        handleLine.setFrameShape(QFrame.VLine)
        handleLine.setFrameShadow(QFrame.Sunken)
        handleLayout.addWidget(handleLine, 0, Qt.AlignHCenter)

        scrollArea = QScrollArea()
        scrollArea.setWidget(splitter)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.mainLayout.addWidget(scrollArea)

        layout = QHBoxLayout()
        self.revertBtn = QPushButton('Revert')
        self.setBtn = QPushButton('Set')
        self.revertBtn.clicked.connect(self.revertSavedProperties)
        self.setBtn.clicked.connect(self.setAllProperties)
        layout.addWidget(self.revertBtn)
        layout.addWidget(self.setBtn)
        self.mainLayout.addLayout(layout)

        for prop in PGCameraProperties:
            value = self.properties[prop.name]['abs_value']
            self.sliders[prop.name].setValue(value)
            self.spinboxes[prop.name].setValue(value)

            auto = self.properties[prop.name]['auto_manual_mode']
            self.autoBoxes[prop.name].setChecked(auto)


            # by default start off unchecked for the trigger mode
            if(prop == PGCameraProperties.TRIGGER_MODE or
                    prop == PGCameraProperties.TRIGGER_DELAY or
                    prop == PGCameraProperties.FRAME_RATE or
                    prop == PGCameraProperties.TEMPERATURE):
                self.enableBoxes[prop.name].setChecked(False)
            else:
                enable = self.properties[prop.name]['on_off']
                self.enableBoxes[prop.name].setChecked(enable)


            self.setProperty(prop.name)


        self.updateShutterLims()

        self.savedProperties = copy.deepcopy(self.properties)

        self.setLayout(self.mainLayout)
        self.initialized = True


    @pyqtSlot(int)
    def enableProperty(self, state):
        """
        Enables/disables the property corresponding to the checkbox
        :param state: state of the checkbox
        :return:
        """
        box = self.sender()
        prop = box.objectName()

        if state == Qt.Checked:
            enabled = True
        else:
            enabled = False

        if(prop != PGCameraProperties.FRAME_RATE.name):
            # self.labels[prop].setEnabled(enabled)
            self.sliders[prop].setEnabled(enabled)
            self.spinboxes[prop].setEnabled(enabled)
            self.autoBoxes[prop].setEnabled(enabled)

        self.properties[prop]['on_off'] = enabled

        if(prop == PGCameraProperties.FRAME_RATE.name):
            self.updateShutterLims()



        self.propertyChanged.emit(prop)


    @pyqtSlot(int)
    def setAutoAdjust(self, state):
        """
        Sets the property corresponding to the checkbox to auto-adjust
        :param state: state of the checkbox
        :return:
        """
        box = self.sender()
        prop = box.objectName()

        auto = (state == Qt.Checked)

        self.sliders[prop].setEnabled(not auto)
        self.spinboxes[prop].setReadOnly(auto)

        self.properties[prop]['auto_manual_mode'] = auto

        self.propertyChanged.emit(prop)


    @pyqtSlot(str)
    def setProperty(self, prop):
        """
        Updates the property real-time, does nothing if property is invalid
        :param prop: name of property to update
        :return:
        """
        if not prop in self.properties.keys():
            return

        if self.camD.setProperty(self.properties[prop]) == -1:
            self.sliders[prop].setEnabled(False)
            self.spinboxes[prop].setEnabled(False)
            self.autoBoxes[prop].setEnabled(False)
            self.enableBoxes[prop].setEnabled(False)
        else:
            enabled = self.enableBoxes[prop].isChecked()
            auto = self.autoBoxes[prop].isChecked()

            if(prop != PGCameraProperties.FRAME_RATE.name):
                self.sliders[prop].setEnabled(enabled and not auto)
                self.spinboxes[prop].setEnabled(enabled)
                self.spinboxes[prop].setReadOnly(auto)
                self.autoBoxes[prop].setEnabled(enabled)

            self.enableBoxes[prop].setEnabled(True)



    def update_properties(self):
        for prop in PGCameraProperties:
            self.properties[prop.name] = self.camD.getProperty(prop.value)


    def updateProperty(self, newValue):
        """
        Updates the given property value
        :param newValue: value of the new setting for the property, can be float or int
        :return:
        """

        sender = self.sender()
        prop = sender.objectName()

        if prop not in self.properties.keys():
            return  # invalid property

        self.properties[prop]['abs_value'] = newValue

        if self.sliders[prop].value() != newValue:
            self.sliders[prop].setValue(newValue)

        if self.spinboxes[prop].value() != newValue:
            self.spinboxes[prop].setValue(newValue)

        if (PGCameraProperties.FRAME_RATE.name in self.enableBoxes) \
                and self.enableBoxes[PGCameraProperties.FRAME_RATE.name].isChecked() \
                and prop == PGCameraProperties.FRAME_RATE.name:
            # print('Changed FR: ' + str(newValue))
            maxShutter = 1000/newValue
            self.sliders[PGCameraProperties.SHUTTER.name].setRange(0.01, maxShutter)
            self.spinboxes[PGCameraProperties.SHUTTER.name].setRange(0.01, maxShutter)

        self.propertyChanged.emit(prop)


    def refreshProperties(self):
        """
        Updates properties which auto-adjust with the current values after the frame is received
        :return:
        """
        if not self.initialized:
            return

        for prop in PGCameraProperties:
            auto = self.autoBoxes[prop.name].isChecked()

            if auto:
                # update the property with that from the camera
                propVal = self.camD.getProperty(prop.value)

                if propVal == -1:
                    return

                self.properties[prop.name] = propVal

                # update the GUI with the properties
                newValue = self.properties[prop.name]['abs_value']

                if self.sliders[prop.name].value() != newValue:
                    self.sliders[prop.name].setValue(newValue)

                if self.spinboxes[prop.name].value() != newValue:
                    self.spinboxes[prop.name].setValue(newValue)


    def setAllProperties(self):
        """
        Saves the current properties for easy reversion, then sets the properties
        :return:
        """
        self.savedProperties = copy.deepcopy(self.properties)

        for prop in self.properties.keys():
            self.setProperty(prop)


    def revertSavedProperties(self):
        """
        Loads the previously saved properties
        :return:
        """
        if(self.savedProperties is None or len(self.savedProperties) == 0):
            return


        self.properties = copy.deepcopy(self.savedProperties)


        for prop in PGCameraProperties:
            if(prop not in self.properties):
                continue

            enable = self.properties[prop.name]['on_off']
            self.enableBoxes[prop.name].setChecked(enable)

            auto = self.properties[prop.name]['auto_manual_mode']
            # print(prop.name + ":" + str(auto))
            self.autoBoxes[prop.name].setChecked(auto)

            value = self.properties[prop.name]['abs_value']
            self.sliders[prop.name].setValue(value)
            self.spinboxes[prop.name].setValue(value)


    def updateShutterLims(self):
        enabled = self.enableBoxes[PGCameraProperties.FRAME_RATE.name].isChecked()

        if not enabled:
            if self.cam_mode == 7:
                self.sliders[PGCameraProperties.SHUTTER.name].setMaximum(32000)
                self.spinboxes[PGCameraProperties.SHUTTER.name].setMaximum(32000)
            else:
                self.sliders[PGCameraProperties.SHUTTER.name].setMaximum(8000)
                self.spinboxes[PGCameraProperties.SHUTTER.name].setMaximum(8000)

        else:
            fr = self.properties[PGCameraProperties.FRAME_RATE.name]['abs_value']
            maxShutter = 1000 / fr
            self.sliders[PGCameraProperties.SHUTTER.name].setRange(0.01, maxShutter)
            self.spinboxes[PGCameraProperties.SHUTTER.name].setRange(0.01, maxShutter)