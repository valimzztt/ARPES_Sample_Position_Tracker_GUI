import sys

from PyQt5.QtWidgets import QApplication, QLabel, QDesktopWidget
from PyQt5.QtCore import QTimer
from mainwindow import MainWindow


def main():
    qt_app = QApplication(sys.argv)
    mainwindow = MainWindow()

    # needs to be started up after a certain time for video feed to stabilize
    # QTimer.singleShot(mainwindow.STARTUP_TIME, mainwindow.show)

    qt_app.exec_()

if __name__ == '__main__':
    sys.exit(main())


