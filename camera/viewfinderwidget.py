from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import QImage, QPalette, QPainter, QRegion, QImageWriter
from PyQt5.QtCore import QRect, QPoint, Qt, pyqtSlot, pyqtSignal
from utilities import ErrorPriority
import numpy as np
import time
import cv2


"""
This class implements the specifications for QAbstractVideoSurface
"""
class VideoWidgetSurface(QAbstractVideoSurface):

    def __init__(self, widget, parent = None):
        self.widget = widget
        # default is a blank screen
        self.currentFrame = QVideoFrame()
        self.targetRect = QRect()
        super().__init__(parent=parent)

    """
    From the supportedPixelFormats() function we return a list of pixel formats the surface can paint. The order of the list hints at which formats are preferred by the surface.
    These are the Flea-3's supported formats

    Since we don't support rendering using any special frame handles we don't return any pixel formats if handleType is not QAbstractVideoBuffer::NoHandle.
    """
    def supportedPixelFormats(self, type=None):
        if(type == QAbstractVideoBuffer.NoHandle):
            return [QVideoFrame.Format_RGB24,
                    QVideoFrame.Format_Y8,
                    QVideoFrame.Format_Y16,
                    QVideoFrame.Format_YUV444,
                    QVideoFrame.Format_CameraRaw]
        else:
            return []

    """
    In isFormatSupported() we test if the frame type of a surface format maps to a valid QImage format,
    that the frame size is not empty, and the handle type is QAbstractVideoBuffer::NoHandle.
    Note that the QAbstractVideoSurface implementation of isFormatSupported() will verify that the list of supported
    pixel formats returned by supportedPixelFormats(format.handleType()) contains the pixel format and that the size is
     not empty so a reimplementation wasn't strictly necessary in this case.
    """
    def isFormatSupported(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()

        return imageFormat != QImage.Format_Invalid and (not size.isEmpty()) and format.handleType() == QAbstractVideoBuffer.NoHandle

    def start(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()

        if (imageFormat != QImage.Format_Invalid and not size.isEmpty()):
            self.imageFormat = imageFormat
            self.imageSize = size
            self.sourceRect = format.viewport()

            super().start(format)

            self.widget.updateGeometry()
            self.updateVideoRect()

            return True
        else:
            return False

    def updateVideoRect(self):
        size = self.surfaceFormat().sizeHint()
        size.scale(self.widget.size().boundedTo(size), Qt.KeepAspectRatio)

        self.targetRect = QRect(QPoint(0, 0), size)
        self.targetRect.moveCenter(self.widget.rect().center())

    def present(self, frame):
        # print(self.surfaceFormat().pixelFormat())
        # print(frame.pixelFormat())
        if(self.surfaceFormat().pixelFormat() != frame.pixelFormat() or self.surfaceFormat().frameSize() != frame.size()):
            self.setError(self.IncorrectFormatError)
            self.stop()
            return False
        else:
            self.currentFrame = frame
            self.widget.repaint(self.targetRect)
            return True

    def paint(self, painter):
        if (self.currentFrame.map(QAbstractVideoBuffer.ReadOnly)):
            oldTransform = painter.transform()

            if self.surfaceFormat().scanLineDirection() == QVideoSurfaceFormat.BottomToTop:
                painter.scale(1,-1)
                painter.translate(0, -self.widget.height())

            image = QImage(self.currentFrame.bits(),
                           self.currentFrame.width(),
                           self.currentFrame.height(),
                           self.currentFrame.bytesPerLine(),
                           self.imageFormat)

            painter.drawImage(self.targetRect, image, self.sourceRect)
            painter.setTransform(oldTransform)
            self.currentFrame.unmap()
        else: #if invalid frame received
            painter.drawText(self.targetRect, Qt.AlignCenter, "No feed...\nCheck Camera Status")


    def stop(self):
        self.currentFrame = QVideoFrame()
        self.targetRect = QRect()
        super().stop()
        self.widget.update()


    def videoRect(self):
        return self.targetRect


"""
The ViewfinderWidget class uses the VideoWidgetSurface class to implement a video widget.
"""
class ViewfinderWidget(QWidget):
    """"
    This class is the widget that holds the viewport into the camera
    """
    sampleClicked = pyqtSignal(int, int)

    # time in ms to wait before restarting the stream
    RESTART_TIME = 1

    erroredOut = pyqtSignal(str, ErrorPriority)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        # self.setAttribute(Qt.WA_PaintOnScreen, True)
        palette = self.palette()
        palette.setColor(QPalette.Background, Qt.black)
        self.setPalette(palette)

        self.surface = VideoWidgetSurface(self)
        self.lastShowTime = time.time()

        # rate per second at which camera view is refreshed and re-drawn (since drawing takes time)
        self.FRAME_RATE = 24.0  # anything above 24 is considered smooth motion


    def closeEvent(self, QCloseEvent):
        del self.surface

    def videoSurface(self):
        return self.surface

    def sizeHint(self):
        return self.surface.surfaceFormat().sizeHint()

    def paintEvent(self, event):
        painter = QPainter(self)

        if(self.surface.isActive()):
            videoRect = self.surface.videoRect()

            if(not videoRect.contains(event.rect())):
                region = event.region()
                region.subtracted(QRegion(videoRect))

                brush = self.palette().window()

                for rect in region.rects():
                    painter.fillRect(rect, brush)

            self.surface.paint(painter)
        else:
            painter.fillRect(event.rect(), self.palette().window())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.surface.updateVideoRect()

    @pyqtSlot(np.ndarray)
    def processFrame(self, frame):
        """
        Process the Numpy array from a camera to display it on the surface
        :param frame: the numpy pixel array from the camera daemon
        :return:
        """

        # this updates the video display according to the frame rate of the camera, otherwise it is unnecessary to update the feed any faster
        if (time.time() - self.lastShowTime < 1.0/self.FRAME_RATE):
            return

        # construct QImage
        qIm = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

        # construct a video frame from the QImage
        vidFrame = QVideoFrame(qIm)
        vidFrame.map(QAbstractVideoBuffer.ReadOnly)

        # present on video surface
        self.surface.present(vidFrame)

        self.currImg = qIm

        self.lastShowTime = time.time()

    @pyqtSlot()
    def saveCurrentFrame(self):
        filename, formatstr = QFileDialog.getSaveFileName(parent=self, caption="Save Image", directory="untitled.png",
                                           filter="PNG (*.png);;JPEG (*.jpg);;Bitmap (*.bmp);;Portable Bitmap (*.pbm);;Portable Graymap (*.pgm);;Portable Pixmap (*.ppm);;X11 Bitmap (*.xbm);;X11 Pixmap (*.xpm)")
        if(len(filename) == 0):
            return

        if(formatstr == "PNG (*.png)"):
            formatstr = "png"
        elif formatstr == "JPEG (*jpg)":
            formatstr = "jpg"
        elif formatstr == "Bitmap (*.bmp)":
            formatstr = "bmp"
        elif formatstr == "Portable Bitmap (*.pbm)":
            formatstr = "pbm"
        elif formatstr == "Portable Graymap (*.pgm)":
            formatstr = "pgm"
        elif formatstr == "Portable Pixmap (*.ppm)":
            formatstr = "ppm"
        elif formatstr == "X11 Bitmap (*.xbm)":
            formatstr = "xbm"
        elif formatstr == "X11 Pixmap (*.xpm)":
            formatstr = "xpm"
        else:
            self.erroredOut.emit("Invalid format, " + formatstr + ". No image saved.", ErrorPriority.Notice)

        writer = QImageWriter(filename, formatstr.encode('utf-8'))

        if(not writer.canWrite()):
            self.erroredOut.emit("Cannot write image.", ErrorPriority.Notice)

        if(not writer.write(self.currImg)):
            self.erroredOut.emit("Cannot write image. " + writer.errorString(), ErrorPriority.Notice)


    def mousePressEvent(self, event):
        camView = self.parent()
        if camView.selectSampleAct.isChecked():
            videoRect = self.surface.videoRect()
            x, y = (event.x() - videoRect.x(), event.y() - videoRect.y())
            scaled_x, scaled_y = (int(x*self.currImg.width()/videoRect.width()), int(y*self.currImg.height()/videoRect.height()))
            self.sampleClicked.emit(scaled_x, scaled_y)
            camView.selectSampleAct.toggle()
        else:
            return
