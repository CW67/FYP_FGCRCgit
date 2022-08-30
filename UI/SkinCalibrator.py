from VidThread import VideoThread
from superqt import QRangeSlider
from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat import QtCore
from qtrangeslider.qtcompat import QtWidgets as QtW
from qtrangeslider import QLabeledRangeSlider
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from numpy import expand_dims
from PyQt5.QtMultimedia import QCameraInfo

QSS = """
QSlider {
    height: 20px;
    width: 50px;
}
QSlider::groove:horizontal {
    border: 0px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #888, stop:1 #ddd);
    height: 20px;
    border-radius: 10px;
}
QSlider::handle {
    background: qradialgradient(cx:0, cy:0, radius: 1.2, fx:0.35,
                                fy:0.3, stop:0 #eef, stop:1 #002);
    height: 20px;
    width: 20px;
    border-radius: 10px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #227, stop:1 #77a);
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}
QRangeSlider {
    qproperty-barColor: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #227, stop:1 #77a);
}
"""


class calibrationWidget(QtW.QWidget):
    def __init__(self) -> None:
        super(calibrationWidget, self).__init__()

        self.hLow = 0
        self.hHigh = 255

        self.sLow = 0
        self.sHigh = 255

        self.vLow = 0
        self.vHigh = 255

        self.available_cameras = QCameraInfo.availableCameras()  # Getting available cameras

        self.vidConnectFlag = 0

        self.vThread = VideoThread()



        self.range_hslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        self.range_hslider.setMaximumWidth(400)
        self.range_hslider.setRange(0, 255)


        self.range_sslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        self.range_sslider.setMaximumWidth(400)
        self.range_sslider.setRange(0, 255)

        self.range_vslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        self.range_vslider.setMaximumWidth(400)
        self.range_vslider.setRange(0, 255)

        self.loadSeg()


        label1 = QtW.QLabel("Hue Value")
        # label1.setSizePolicy(szp, szp)

        label2 = QtW.QLabel("Saturation Value")
        # label2.setSizePolicy(szp, szp)

        label3 = QtW.QLabel("Brightness Value")
        # label3.setSizePolicy(szp, szp)

        # Video screen
        self.vThread = VideoThread()
        self.video_label = QLabel()
        self.display_width = 320
        self.display_height = 240
        self.video_label.resize(self.display_width, self.display_height)
        self.video_label.setFixedWidth(self.display_width)
        self.video_label.setFixedHeight(self.display_height)
        self.video_label.setStyleSheet("background : black;")

        self.video_label2 = QLabel()
        self.video_label2.resize(self.display_width, self.display_height)
        self.video_label2.setFixedWidth(self.display_width)
        self.video_label2.setFixedHeight(self.display_height)
        self.video_label2.setStyleSheet("background : black;")


        # Button to start video
        self.ss_video = QPushButton()
        self.ss_video.setText('Start video')
        self.ss_video.move(350, 50)
        self.ss_video.resize(150, 50)
        self.ss_video.clicked.connect(self.ClickStartVideo)
        #left.layout().addWidget(self.ss_video)

        #Camera Selector
        camera_selector = QComboBox()
        camera_selector.setStatusTip("Choose camera to take pictures")
        # adding tool tip to it
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        # adding items to the combo box
        camera_selector.addItems([camera.description()
                                  for camera in self.available_cameras])
        # Camera selection function
        camera_selector.activated[int].connect(self.returnSelected)
        camera_selector.setFixedWidth(200)


        #Save button
        self.ss_save = QPushButton()
        self.ss_save.setText('Save configuration')
        self.ss_save.clicked.connect(self.saveSeg)
        self.ss_save.setFixedHeight(150)

        left = QtW.QWidget()
        left.setLayout(QtW.QVBoxLayout())
        left.setContentsMargins(2, 2, 2, 2)

        left.layout().addWidget(self.range_hslider)
        left.layout().addWidget(label1)

        left.layout().addWidget(self.range_sslider)
        left.layout().addWidget(label2)

        left.layout().addWidget(self.range_vslider)
        left.layout().addWidget(label3)

        right = QtW.QWidget()
        right.setLayout(QtW.QVBoxLayout())
        right.layout().addWidget(self.ss_save)

        top = QtW.QWidget()
        top.setLayout(QtW.QVBoxLayout())
        top.layout().addWidget(camera_selector)
        topvideo = QtW.QWidget()
        topvideo.setLayout(QtW.QHBoxLayout())
        topvideo.layout().addWidget(self.video_label)
        topvideo.layout().addWidget(self.video_label2)
        top.layout().addWidget(topvideo)
        top.layout().addWidget(self.ss_video)

        mid = QtW.QWidget()
        mid.setLayout(QtW.QHBoxLayout())

        bottom =QtW.QWidget()
        bottom.setLayout(QtW.QHBoxLayout())
        bottom.layout().addWidget(left)
        bottom.layout().addWidget(right)

        self.range_hslider.valueChanged.connect(lambda e: self.changeH(e))
        self.range_sslider.valueChanged.connect(lambda e: self.changeS(e))
        self.range_vslider.valueChanged.connect(lambda e: self.changeV(e))

        self.setLayout(QtW.QHBoxLayout())
        self.layout().addWidget(top)
        top.layout().addWidget(bottom)
        self.setGeometry(600, 300, 580, 500)
        self.activateWindow()
        self.show()

    ########################################################################################################################
    #                                                   Start/stop Buttons                                                            #
    ########################################################################################################################
    # Activates when Start/Stop video button is clicked to Start (ss_video
    def ClickStartVideo(self):
        # Change label color to light blue
        self.ss_video.clicked.disconnect(self.ClickStartVideo)
        # Change button to stop
        self.ss_video.setText('Stop video')
        self.vThread.change_pixmap_signal.connect(self.update_image)

        # start the thread
        self.vThread.start()
        self.ss_video.clicked.connect(self.vThread.stop)  # Stop the video if button clicked
        self.ss_video.clicked.connect(self.ClickStopVideo)

    # Activates when Start/Stop video button is clicked to Stop (ss_video)
    def ClickStopVideo(self):
        self.vThread.change_pixmap_signal.disconnect()
        self.ss_video.setText('Start video')
        self.ss_video.clicked.disconnect(self.ClickStopVideo)
        self.ss_video.clicked.disconnect(self.vThread.stop)
        self.ss_video.clicked.connect(self.ClickStartVideo)

    ########################################################################################################################
    #                                                   Actions                                                            #
    ########################################################################################################################
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        qt_imgB = self.convert_cv_Base(cv_img)
        self.video_label.setPixmap(qt_img)
        self.video_label2.setPixmap(qt_imgB)

    def update_imageBase(self, cv_img):
        """Updates the image_label with a new opencv image"""

    def convert_cv_qt(self, cv_img):
        lower = np.array([self.hLow, self.sLow, self.vLow], dtype="uint8")
        upper = np.array([self.hHigh, self.sHigh, self.vHigh], dtype="uint8")
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_RGB2HSV)
        # Generate Binary Skin Mask
        skinMask = cv2.inRange(rgb_image, lower, upper)
        skinMask = skinMask.astype("uint8")
        # apply a series of erosions and dilations to the mask
        # using an elliptical kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        # skinMask = cv2.erode(skinMask, kernel, iterations=3)
        skinMask = cv2.dilate(skinMask, kernel, iterations=5)
        skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
        bin_img = cv2.cvtColor(skinMask, cv2.COLOR_GRAY2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        # skinMask = skinMask.astype(np.int64)
        convert_to_Qt_format = QtGui.QImage(bin_img.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        # p = convert_to_Qt_format.scaled(801, 801, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def convert_cv_Base(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        # p = convert_to_Qt_format.scaled(801, 801, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def returnSelected(self, param):
        print('The current highlighted index is: ', param)
        self.vThread.setCam(param)
        if self.vidConnectFlag == 1:
            self.vThread.stop()
            self.ClickStopVideo()

    def saveSeg(self):
        arr = [self.hLow, self.sLow, self.vLow, self.hHigh, self.sHigh, self.vHigh]
        with open('segSettings.txt', 'w') as filehandle:
            for listitem in arr:
                filehandle.write('%s\n' % listitem)


    def loadSeg(self):
        vals = []
        # open file and read the content in a list
        with open('segSettings.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]

                # add item to the list
                # add item to the list
                vals.append(currentPlace)
            self.hLow = float(vals[0])
            self.sLow = float(vals[1])
            self.vLow = float(vals[2])
            self.hHigh = float(vals[3])
            self.sHigh = float(vals[4])
            self.vHigh = float(vals[5])
            self.range_hslider.setValue((self.hLow, self.hHigh))
            self.range_sslider.setValue((self.sLow, self.sHigh))
            self.range_vslider.setValue((self.vLow, self.vHigh))
# =======================Slider Actions=============================

    def changeH(self, e):
        self.hLow = e[0]
        self.hHigh = e[1]

    def changeS(self, e):
        self.sLow = e[0]
        self.sHigh = e[1]

    def changeV(self, e):
        self.vLow = e[0]
        self.vHigh = e[1]


# ===================


if __name__ == "__main__":

    import sys
    from pathlib import Path

    dest = Path("screenshots")
    dest.mkdir(exist_ok=True)

    app = QtW.QApplication([])
    demo = calibrationWidget()

    if "-snap" in sys.argv:
        import platform

        QtW.QApplication.processEvents()
        demo.grab().save(str(dest / f"demo_{platform.system().lower()}.png"))
    else:
        app.exec_()
