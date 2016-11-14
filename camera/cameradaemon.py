from enum import Enum, unique

import flycapture2 as fc2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QMutex, QMutexLocker
from scipy.signal import find_peaks_cwt

from camera.cameraconfigwidget import CameraConfigureWidget
from utilities import ErrorPriority
import cv2


@unique
class PGCameraStates(Enum):
    Invalid = 0
    Connected = 1
    Streaming = 2
    Disconnected = 3

@unique
class ImageMode(Enum):
    Processed = 0
    Original = 1
    Threshold = 2


class PGCameraDaemon(QThread):
    """
    This class implements a camera thread for use with Point Grey Flea-3 Camera.

    This class is instantiated in the main GUI thread, but the run() function operates as a separate thread.

    This class also processes each frame as it comes in.
    """
    receivedFrame = pyqtSignal(np.ndarray)
    erroredOut = pyqtSignal(str, ErrorPriority)
    stateChanged = pyqtSignal(PGCameraStates, PGCameraStates)
    camConnected = pyqtSignal(dict)
    frameProcessed = pyqtSignal(dict)
    sampleDetected = pyqtSignal(int, int, int, int, int)

    ERROR_COUNT_LIMIT = 10 #TODO set to frame rate limit

    def _monitorForErrors(changeStateToInvalid=True, priority=ErrorPriority.Notice):
        # This decorator wraps the function to emit errors if an exception is raised.
        # The argument controls whether to change the state to invalid or not.
        def errorWrapper(fn):
            # This adds a forwarding of error strings to the GUI thread when fn is called
            # If an error occured then -1 is returned
            def wrapped(self, *args, **kwargs):
                try:
                    return fn(self, *args, **kwargs)
                except Exception as e:
                    self.erroredOut.emit("From func '" + fn.__name__ + "': " + str(e), priority)
                    if changeStateToInvalid:
                        self.changeStateTo(PGCameraStates.Invalid)
                    return -1

            return wrapped
        return errorWrapper


    def __init__(self, parent=None, cam_index=0, cam_mode=fc2.MODE_0, cam_x = 0, cam_y = 0, cam_w=1280, cam_h=960, cam_pixformat=fc2.PIXEL_FORMAT_RGB8):
        """
        Starts a camera context with the given camera information
        :param cam_index: addStr of the camera
        :param cam_mode: fc2 mode to use, default is MODE_0. See FlyCapture2 documentation for more details
        :param cam_w: width of camera feed
        :param cam_h: height of camera feed
        :param cam_pixformat: pixel format to use. By default, uses a 24-bit RGB scheme.
        """
        QThread.__init__(self, parent)

        self.statemutex = QMutex()
        self.stopmutex = QMutex()
        self.stop = False

        self.state = PGCameraStates.Invalid

        self.data = dict() # data for plotting

        self.threshold = 60
        self.area = 500
        self.areaBuffer = 100
        self.aspect_ratio = 1
        self.imageMode = ImageMode.Processed

        self.context = fc2.Context()
        self.changeStateTo(PGCameraStates.Disconnected)

        try:
            self.currentIndex = cam_index
            self.context.connect(*self.context.get_camera_from_index(cam_index))

            CameraConfigureWidget.usedCamIndices.append(cam_index)

            self.context.set_format7_configuration(cam_mode, cam_x, cam_y, cam_w, cam_h, cam_pixformat)
            self.changeStateTo(PGCameraStates.Connected)
        except Exception as e:
            self.erroredOut.emit(str(e), ErrorPriority.Critical)
            self.changeStateTo(PGCameraStates.Invalid)




    def __del__(self):
        self.stopmutex.lock()
        self.stop = True
        self.stopmutex.unlock()
        # self.wait()

    def changeStateTo(self, newState):
        """
        Used to emit the state change signal
        :param newState:
        :return:
        """

        # only emit when state changes
        if(self.state == newState):
            return

        self.statemutex.lock()
        oldState = self.state
        self.state = newState
        self.statemutex.unlock()
        self.stateChanged.emit(newState, oldState)

        if(newState == PGCameraStates.Connected or newState == PGCameraStates.Streaming):
            try:
                self.camConnected.emit(self.context.get_camera_info())
            except Exception as e:
                self.erroredOut.emit(str(e), ErrorPriority.Notice)
        else:
            blank = dict(model_name="---",
                         firmware_version="---",
                         sensor_info="---",
                         sensor_resolution="---",
                         serial_number="---",
                         vendor_name="---")
            self.camConnected.emit(blank)

    @_monitorForErrors()
    def changeCameraConfig(self, cam_index=0, cam_mode=fc2.MODE_0, cam_x = 0, cam_y = 0, cam_w=1280, cam_h=960, cam_pixformat=fc2.PIXEL_FORMAT_RGB8):
        """
        If the camera daemon is stopped, then change the configuration settings, otherwise, emit error message.
        :param cam_index: addStr of the camera
        :param cam_mode: fc2 mode to use, default is MODE_0. See FlyCapture2 documentation for more details
        :param cam_w: width of camera feed
        :param cam_h: height of camera feed
        :param cam_pixformat: pixel format to use. By default, uses a 24-bit RGB scheme.
        :return:
        """
        if self.state == PGCameraStates.Streaming or self.isRunning():
            self.erroredOut.emit('Cannot change camera configuration while streaming!', ErrorPriority.Notice)
        else: #if the thread is not running
            # self.context.stop_capture()
            self.context.disconnect()
            if cam_index in CameraConfigureWidget.usedCamIndices and cam_index != self.currentIndex:
                self.erroredOut.emit('Camera Index ({0}), is already in use!'.format(cam_index), ErrorPriority.Critical)
                self.changeStateTo(PGCameraStates.Invalid)
            else:
                self.context.connect(*self.context.get_camera_from_index(cam_index))
                self.context.set_format7_configuration(cam_mode, cam_x, cam_y, cam_w, cam_h, cam_pixformat)
                self.changeStateTo(PGCameraStates.Connected)

            if(self.state != PGCameraStates.Connected):
                self.context.disconnect()
            else:

                if self.currentIndex in CameraConfigureWidget.usedCamIndices:
                    CameraConfigureWidget.usedCamIndices.remove(self.currentIndex)
                CameraConfigureWidget.usedCamIndices.append(cam_index)
                self.currentIndex = cam_index

    @_monitorForErrors(False)
    def getFrameRate(self):
        """
        Returns the frame rate as a number
        :return: the frame rate of the current camera configuration, otherwise if there is an error it gives -1
        """
        if self.state == PGCameraStates.Disconnected or self.state == PGCameraStates.Invalid:
            self.erroredOut.emit('Cannot get frame rate, camera is disconnected!', ErrorPriority.Notice)
            # impossible frame_rate
            return -1
        else:
            p = self.context.get_property(fc2.FRAME_RATE)
            frame_rate = p['abs_value']
            # print(frame_rate)
            return frame_rate

    @_monitorForErrors(False)
    def getProperty(self, prop):
        """
        :param prop: Number of property type, e.g. GAMMA
        :return: the dictionary of the property if valid, otherwise return -1
        """
        if self.state == PGCameraStates.Disconnected or self.state == PGCameraStates.Invalid:
            self.erroredOut.emit('Cannot get property, {0}, camera is disconnected!'.format(prop), ErrorPriority.Notice)
            return -1
        else:
            p = self.context.get_property(prop)
            return p

    @_monitorForErrors(False)
    def setProperty(self, prop):
        """
        :param prop: Dictionary with property values
        :return:
        """
        if self.state == PGCameraStates.Disconnected or self.state == PGCameraStates.Invalid:
            self.erroredOut.emit('Cannot set property, {0}, camera is disconnected!'.format(prop), ErrorPriority.Notice)
        else:
            self.context.set_property(**prop)


    @pyqtSlot(bool)
    def stream(self, play):
        """
        Stop streaming frames from the camera
        :return:
        """
        locker = QMutexLocker(self.stopmutex)
        self.stop = not play
        if(play and not self.isRunning()):
            self.start()


    def run(self):
        """
        Runs the loop to get a frame from the camera
        :return:
        """

        # check that the camera is connected
        self.statemutex.lock()
        if(self.state != PGCameraStates.Connected):
            self.erroredOut.emit('Cannot start stream, camera is disconnected!', ErrorPriority.Notice)
            self.statemutex.unlock()
            return #quit if not connected
        #else
        self.statemutex.unlock()


        # start recording, exit if failed
        try:
            self.context.start_capture()
        except Exception as e:
            self.erroredOut.emit(str(e), ErrorPriority.Critical)
            self.changeStateTo(PGCameraStates.Invalid)
            return


        self.stopmutex.lock()
        self.stop = False
        self.stopmutex.unlock()

        self.changeStateTo(PGCameraStates.Streaming)

        # create empty image for holding camera data
        im = fc2.Image()

        errCount = 0

        while not self.stop:

            #load image from camera
            try:
                self.context.retrieve_buffer(im)
            except Exception as e:
                # skip this loop
                errCount += 1

                # error out if it cannot retrieve the buffer for too long
                if(errCount >= self.ERROR_COUNT_LIMIT):
                    self.erroredOut.emit(str(e), ErrorPriority.Critical)
                    self.erroredOut.emit('Error counter ({0}) exceeded.'.format(self.ERROR_COUNT_LIMIT), ErrorPriority.Warning)
                    self.changeStateTo(PGCameraStates.Disconnected)
                    break
                else:
                    continue
            else:
                errCount = 0

            # Create color matrix
            img = np.array(im)

            if(self.imageMode == ImageMode.Original):
                self.receivedFrame.emit(img)

            img = self.findSample(img)

            if(self.imageMode == ImageMode.Processed):
                self.receivedFrame.emit(img)
            # self.msleep(100)

        if(self.stop):
            self.context.stop_capture()
            self.changeStateTo(PGCameraStates.Connected) # this is reached when loop exits in a valid way
        return

    @_monitorForErrors()
    def findSample(self, img):
        # Our operations on the frame come here
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 9)
        ret, thresh = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY)

        if (self.imageMode == ImageMode.Threshold):
            self.receivedFrame.emit(np.stack([thresh, thresh, thresh], axis=2))

        image, self.contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        matches = []
        sides = []
        for cnt in self.contours:

            area = cv2.contourArea(cnt)
            # print(area)

            if (abs(area - self.area) <= self.areaBuffer):
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                # print(aspect_ratio)

                diff_to_sample = abs(aspect_ratio - self.aspect_ratio)

                if (diff_to_sample < 0.5):
                    matches.append(cnt)
            elif (area > 12000):
                image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
                sides.append(cnt)
        if len(sides) == 2:
            x1, y1, w1, h1 = cv2.boundingRect(sides[0])
            x2, y2, w2, h2 = cv2.boundingRect(sides[1])

            for cnt in matches:
                x, y, w, h = cv2.boundingRect(cnt)

                # if sample candidate between the shields
                if (x1 < x2 and x1 <= x <= x2) or (x2 < x1 and x2 <= x <= x1):
                    area = cv2.contourArea(cnt)
                    self.sampleDetected.emit(int(x+w/2), int(y+h/2), w, h, area)
                    image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        else:
            for cnt in matches:
                x, y, w, h = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)

                self.sampleDetected.emit(int(x+w/2), int(y+h/2), w, h, area)

                image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return img


    @pyqtSlot(int)
    def changeImageMode(self, mode):
        self.imageMode = ImageMode(mode)

    @pyqtSlot(int)
    def changeThreshold(self, thresh):
        self.threshold = thresh

    @pyqtSlot(int, int)
    def setSample(self, sample_x, sample_y):
        # Find the contour under the mouse click and extract relevant parameters from it
        for cnt in self.contours:
            x, y, w, h = cv2.boundingRect(cnt)

            if(sample_x > x and sample_x < x+w and sample_y > y and sample_y < y+h):
                area = cv2.contourArea(cnt)
                self.area = area
                self.aspect_ratio = float(w) / h
                return


    @pyqtSlot(float)
    def changeAreaBuffer(self, areabuffer):
        self.areaBuffer = areabuffer

    _monitorForErrors = staticmethod(_monitorForErrors)