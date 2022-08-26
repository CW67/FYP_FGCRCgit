
from superqt import QRangeSlider
from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat import QtCore
from qtrangeslider.qtcompat import QtWidgets as QtW
from qtrangeslider import QLabeledRangeSlider
from UI.UI import VideoThread


QSS = """
QSlider {
    min-height: 20px;
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
        range_hslider.setValue((0, 100))

        range_sslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        range_sslider.setValue((0, 100))

        range_vslider = QLabeledRangeSlider(QtCore.Qt.Horizontal)
        range_vslider.setValue((0, 100))


        szp = QtW.QSizePolicy.Maximum
        left = QtW.QWidget()
        left.setLayout(QtW.QVBoxLayout())
        left.setContentsMargins(2, 2, 2, 2)
        label1 = QtW.QLabel("Hue Value")
        label1.setSizePolicy(szp, szp)

        label2 = QtW.QLabel("Saturation Value")
        label2.setSizePolicy(szp, szp)

        label3 = QtW.QLabel("Brightness Value")
        label3.setSizePolicy(szp, szp)


        left.layout().addWidget(range_hslider)
        left.layout().addWidget(label1)

        left.layout().addWidget(range_sslider)
        left.layout().addWidget(label2)

        left.layout().addWidget(range_vslider)
        left.layout().addWidget(label3)

        range_vslider.valueChanged.connect(lambda e: print("doubslider valuechanged", e))

        self.setLayout(QtW.QHBoxLayout())
        self.layout().addWidget(left)
        self.setGeometry(600, 300, 580, 300)
        self.activateWindow()
        self.show()


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