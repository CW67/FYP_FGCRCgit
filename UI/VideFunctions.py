from PyQt5.QtCore import pyqtSignal,QThread
import cv2
import numpy as np

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        #self._pnum = 'http://0.0.0.0:4747/mjpegfeed?640x480'
        self._pnum = 0

    def setCam(self, cnum):
        self._pnum = cnum


    def run(self):
        # capture from web cam
        self._run_flag = True
        self.cap = cv2.VideoCapture(self._pnum)
        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        self.cap.release()


    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False