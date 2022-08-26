from PyQt5 import QtGui
from PyQt5.QtWidgets import  QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraImageCapture
from PyQt5.QtWidgets import *
import sys
from InputDialog import InputDialog
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from plyer import notification


### Video player made for the GUI, credit to Evgeny Fomin and Antonio Domènech (As seen on github https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1)
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self._pnum = 0

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


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.available_cameras = QCameraInfo.availableCameras()  # Getting available cameras
        cent = QDesktopWidget().availableGeometry().center()  # Finds the center of the screen
        self.setStyleSheet("background-color: white;")
        self.resize(1400, 800)
        self.frameGeometry().moveCenter(cent)
        self.setWindowTitle('F.Move')
        self.initWindow()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        self.show()



########################################################################################################################
#                                                   GUI Elements                                                            #
########################################################################################################################
    def initWindow(self):
        # create the video capture thread
        self.thread = VideoThread()


        # Button to start video
        self.ss_video = QPushButton(self)
        self.ss_video.setText('Start video')
        self.ss_video.move(350, 50)
        self.ss_video.resize(150, 50)
        self.ss_video.clicked.connect(self.ClickStartVideo)

        # creating a tool bar
        toolbar = QToolBar("Camera Tool Bar")
        self.addToolBar(toolbar)
        camera_selector = QComboBox()
        camera_selector.setStatusTip("Choose camera to take pictures")
        # adding tool tip to it
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        # adding items to the combo box
        camera_selector.addItems([camera.description()
                                  for camera in self.available_cameras])
        # adding this to tool bar
        toolbar.addWidget(camera_selector)

        button_action = QAction("Camera settings", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.showdialog)
        toolbar.addAction(button_action)

        # Status bar
        self.status = QStatusBar()
        self.status.setStyleSheet("background : lightblue;")  # Setting style sheet to the status bar
        self.setStatusBar(self.status)  # Adding status bar to the main window
        self.status.showMessage('Ready to start')

        #Video screen
        self.image_label = QLabel(self)
        self.disply_width = 300
        self.display_height = 250
        self.image_label.resize(self.disply_width, self.display_height)
        self.image_label.setStyleSheet("background : black;")
        self.image_label.move(10, 40)



########################################################################################################################
#                                                   Start/stop Buttons                                                            #
########################################################################################################################
    # Activates when Start/Stop video button is clicked to Start (ss_video
    def ClickStartVideo(self):
        # Change label color to light blue
        self.ss_video.clicked.disconnect(self.ClickStartVideo)
        self.status.showMessage('Video Running...')
        # Change button to stop
        self.ss_video.setText('Stop video')
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)

        # start the thread
        self.thread.start()
        self.ss_video.clicked.connect(self.thread.stop)  # Stop the video if button clicked
        self.ss_video.clicked.connect(self.ClickStopVideo)

    # Activates when Start/Stop video button is clicked to Stop (ss_video)
    def ClickStopVideo(self):
        self.thread.change_pixmap_signal.disconnect()
        self.ss_video.setText('Start video')
        self.status.showMessage('Ready to start')
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
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        #p = convert_to_Qt_format.scaled(801, 801, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

####################################################################################
    def showdialog(self):
        self.dialog = InputDialog( labels=["First", "Second"])
        self.dialog.show()
        if self.dialog.exec():
            print(self.dialog.getInputs())

    def showNoti(selfs):
        # import win10toast
        from win10toast import ToastNotifier
        # create an object to ToastNotifier class
        n = ToastNotifier()
        n.show_toast("GEEKSFORGEEKS", "You got notification",  threaded=True)


###################################################CAMERA SELECTION======================================================
    # getter method
    def get_camera(self):
        return self._pnum

    # setter method
    def set_camera(self, x):
        self._pnum = x
##########################################################################################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
   #win.show()
    sys.exit(app.exec())