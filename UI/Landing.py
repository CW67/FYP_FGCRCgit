from VidThread import VideoThread
from superqt import QRangeSlider
from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat import QtCore
from qtrangeslider.qtcompat import QtWidgets as QtW
from qtrangeslider import QLabeledRangeSlider
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from numpy import expand_dims

QSS = """
QLabel {
    font-size: 40px;
}
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
        super().__init__()
        self.setStyleSheet(QSS)
        left = QtW.QWidget()
        left.setLayout(QtW.QVBoxLayout())
        left.setContentsMargins(2, 2, 2, 2)
        label1 = QtW.QLabel("Hue Value")
        # label1.setSizePolicy(szp, szp)

        label2 = QtW.QLabel("Saturation Value")
        # label2.setSizePolicy(szp, szp)

        label3 = QtW.QLabel("Brightness Value")
        # label3.setSizePolicy(szp, szp)

        # Video screen
        left.layout().addWidget(label1)

        left.layout().addWidget(label2)

        left.layout().addWidget(label3)


        top = QtW.QWidget()
        top.setLayout(QtW.QVBoxLayout())

        bottom =QtW.QWidget()
        bottom.setLayout(QtW.QHBoxLayout())
        bottom.layout().addWidget(left)


        self.setLayout(QtW.QHBoxLayout())
        self.layout().addWidget(top)
        top.layout().addWidget(bottom)
        self.setGeometry(600, 300, 580, 800)
        self.activateWindow()
        self.show()


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
