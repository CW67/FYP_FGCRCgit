
from superqt import QRangeSlider
from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat import QtCore
from qtrangeslider.qtcompat import QtWidgets as QtW
from qtrangeslider import QLabeledRangeSlider
from UI import VideoThread
from PyQt5 import QtGui
from PyQt5.QtWidgets import  QLabel, QPushButton
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread


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


class DemoWidget(QtW.QWidget):
    def __init__(self) -> None:
        super().__init__()

        range_hslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        range_hslider.setMaximumWidth(400)
        range_hslider.setValue((0, 100))

        range_sslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        range_sslider.setMaximumWidth(400)
        range_sslider.setValue((0, 100))

        range_vslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        range_vslider.setMaximumWidth(400)
        range_vslider.setValue((0, 100))


        szp = QtW.QSizePolicy.Maximum
        left = QtW.QWidget()
        left.setLayout(QtW.QVBoxLayout())
        left.setContentsMargins(2, 2, 2, 2)
        label1 = QtW.QLabel("Hue Value")
        #label1.setSizePolicy(szp, szp)

        label2 = QtW.QLabel("Saturation Value")
        #label2.setSizePolicy(szp, szp)

        label3 = QtW.QLabel("Brightness Value")
        #label3.setSizePolicy(szp, szp)


        left.layout().addWidget(range_hslider)
        left.layout().addWidget(label1)

        left.layout().addWidget(range_sslider)
        left.layout().addWidget(label2)

        left.layout().addWidget(range_vslider)
        left.layout().addWidget(label3)

        range_vslider.valueChanged.connect(lambda e: print("doubslider valuechanged", e))


        #Video screen
        self.vThread = VideoThread()
        self.image_label = QLabel()
        self.display_width = 300
        self.display_height = 250
        self.image_label.resize(self.display_width, self.display_height)
        self.image_label.setStyleSheet("background : black;")
        left.layout().addWidget(self.image_label)

        # Button to start video
        self.ss_video = QPushButton()
        self.ss_video.setText('Start video')
        self.ss_video.move(350, 50)
        self.ss_video.resize(150, 50)
        self.ss_video.clicked.connect(self.ClickStartVideo)
        left.layout().addWidget(self.ss_video)

        self.setLayout(QtW.QHBoxLayout())
        self.layout().addWidget(left)
        self.setGeometry(600, 300, 580, 800)
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
        self.vThread = VideoThread()
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
        self.ss_video.clicked.disconnect(self.thread.stop)
        self.ss_video.clicked.connect(self.ClickStartVideo)

########################################################################################################################
#                                                   Actions                                                            #
########################################################################################################################
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)


    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        #p = convert_to_Qt_format.scaled(801, 801, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == "__main__":

    import sys
    from pathlib import Path

    dest = Path("screenshots")
    dest.mkdir(exist_ok=True)

    app = QtW.QApplication([])
    demo = DemoWidget()

    if "-snap" in sys.argv:
        import platform

        QtW.QApplication.processEvents()
        demo.grab().save(str(dest / f"demo_{platform.system().lower()}.png"))
    else:
        app.exec_()