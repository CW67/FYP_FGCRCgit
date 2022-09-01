
from PyQt5.QtWidgets import *
import sys
from InputDialog import InputDialog
from SkinCalibrator import *
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QEventLoop, QTimer
from VidThread import VideoThread
from Predictor import *
from threading import Thread
import time
from collections import deque



### Video player made for the GUI, credit to Evgeny Fomin and Antonio Domènech (As seen on github https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1)


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.available_cameras = QCameraInfo.availableCameras()  # Getting available cameras
        cent = QDesktopWidget().availableGeometry().center()  # Finds the center of the screen
        self.camThread = VideoThread()
        self.vidConnectFlag = 0
        self.setStyleSheet("background-color: white;")
        self.resize(1400, 800)
        self.frameGeometry().moveCenter(cent)
        self.setWindowTitle('F.Move')
        self.initWindow()
        self.setMaximumSize(1400, 800)
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint | Qt.WindowStaysOnTopHint)

        self.show()
        self.gesture_message = deque([], maxlen=1)
        self.mode_status = deque([], maxlen=1)
        self.predictor = Predictor(self.gesture_message, self.mode_status)
        self.predFlag = False
        self.predictor.addEventListener("Hello", self.foo)
        self.predictor.addEventListener("col change", self.colChange)
        self.sImg_shape = (480, 640, 3)
        self.sImg = np.empty(self.sImg_shape)
        #self.setGeometry(0, 0, 1000, 1000)

#########l###############################################################################################################
#                                                   GUI Elements                                                            #
###########################################################         #############################################################
    def initWindow(self):
        # create the video capture thread

        # Button to start video
        self.ss_video = QPushButton(self)
        self.ss_video.setText('Start video')
        self.ss_video.move(350, 50)
        self.ss_video.resize(150, 50)
        self.ss_video.clicked.connect(self.ClickStartVideo)
        #self.ss_video.clicked.connect(self.MakePrediction)

        self.ss_test = QPushButton(self)
        self.ss_test.setText('Make Single Prediction')
        self.ss_test.move(350, 100)
        self.ss_test.resize(150, 50)
        self.ss_test.clicked.connect(self.MakePrediction)
        #self.ss_video.clicked.connect(self.MakePrediction)

        self.ss_pred = QPushButton(self)
        self.ss_pred.setText('Connect controlling')
        self.ss_pred.move(350, 150)
        self.ss_pred.resize(150, 50)
        self.ss_pred.clicked.connect(self.connect_predictor)

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
        # Camera selection function
        camera_selector.activated[int].connect(self.returnHighlighted)
        # adding this to tool bar
        toolbar.addWidget(camera_selector)

        button_camset = QAction("IP Camera", self)
        button_camset.setStatusTip("Manually Input IP Camera")
        button_camset.triggered.connect(self.showdialog)
        toolbar.addAction(button_camset)

        button_skin = QAction("Skin Calibration ", self)
        button_skin.setStatusTip("Calibrate how the system sees you")
        button_skin.triggered.connect(self.showCalibration)
        toolbar.addAction(button_skin)

        # Status bar
        self.status = QStatusBar()
        self.status.setStyleSheet("background : lightblue;")  # Setting style sheet to the status bar
        self.setStatusBar(self.status)  # Adding status bar to the main window
        self.status.showMessage('Ready to start')

        # Video screen
        self.image_label = QLabel(self)
        self.disply_width = 300
        self.display_height = 250
        self.image_label.resize(self.disply_width, self.display_height)
        self.image_label.setStyleSheet("background : black;")
        self.image_label.move(10, 40)

        #Guide Image
        # setting  the geometry of window

        # creating label
        self.glabel = QLabel(self)
        # loading image
        self.pixmap = QPixmap('GNTNew.png')
        # adding image to label
        self.glabel.setPixmap(self.pixmap)
        # Optional, resize label to image size
        self.glabel.resize(self.pixmap.width(),self.pixmap.height())
        self.glabel.move(500, 40)

########################################################################################################################
#                                                   Start/stop Buttons                                                            #
########################################################################################################################
    # Activates when Start/Stop video button is clicked to Start (ss_video

    def ClickStartVideo(self):
        QTimer.singleShot(1, self.bottomRight)
        # Change label color to light blue
        self.ss_video.clicked.disconnect(self.ClickStartVideo)
        self.status.showMessage('Video Running...')
        # Change button to stop
        self.ss_video.setText('Stop video')
        self.camThread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.camThread.start()
        self.predictor.start()
        #self.predictor.start()
        self.ss_video.clicked.connect(self.camThread.stop)  # Stop the video if button clicked
        self.ss_video.clicked.connect(self.ClickStopVideo)
        self.vidConnectFlag = 1
        #self.predFlag = True

    # Activates when Start/Stop video button is clicked to Stop (ss_video)
    def ClickStopVideo(self):
        self.center()
        self.camThread.change_pixmap_signal.disconnect()
        self.ss_video.setText('Start video')
        self.status.showMessage('Ready to start')
        self.ss_video.clicked.disconnect(self.ClickStopVideo)
        self.ss_video.clicked.disconnect(self.camThread.stop)
        self.predictor.stop()
        self.ss_video.clicked.connect(self.ClickStartVideo)
        self.vidConnectFlag = 0




    ########################################################################################################################
    #                                                   Video  Actions                                                            #
    ########################################################################################################################


    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        #print(type(cv_img))
        self.sImg = cv_img
       # print('Predictor Image')
        self.predictor.updateImg(self.sImg)
        qt_img = self.convert_cv_qt(self.sImg)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        # p = convert_to_Qt_format.scaled(801, 801, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    ####################################################################################
    def connect_predictor(self):
        self.predictor.start()
        self.ss_pred.setText('Disconnect controls')
        self.ss_pred.clicked.connect(self.disconnect_predictor)

    def disconnect_predictor(self):
        self.predictor.stop()
        self.ss_pred.setText('Connect controls')
        self.ss_pred.clicked.connect(self.connect_predictor)

    def MakePrediction(self):
        self.predictor.tdebug(self.sImg)

    def showdialog(self):
        self.dialog = InputDialog(labels=["IP", "Password"])
        self.dialog.show()
        if self.dialog.exec():
            print(self.dialog.getInputs())

    def showCalibration(self):
        calibration = calibrationWidget()
        if self.vidConnectFlag == 1:
            self.camThread.stop()
            self.ClickStopVideo()
        calibration.exec_()


    def showNoti(selfs):
        # import win10toast
        from win10toast import ToastNotifier
        # create an object to ToastNotifier class
        n = ToastNotifier()
        n.show_toast("GEEKSFORGEEKS", "You got notification", threaded=True)

    def foo(self):
        self.status.showMessage(self.gesture_message[-1])

    def colChange(self):
        print('current mode in mainui is ')
        print(self.mode_status[0])
        if self.mode_status[0] == 0:
            self.status.setStyleSheet("background : lightblue;")
        elif self.mode_status[0] == 1:
            self.status.setStyleSheet("background : palegoldenrod;")
        else:
            self.status.setStyleSheet("background : palegreen;")

    def topLeft(self):
        # no need to move the point of the geometry rect if you're going to use
        # the reference top left only
        topLeftPoint = QApplication.desktop().availableGeometry().topLeft()
        self.move(topLeftPoint)

    def bottomRight(self):
        self.setGeometry(0, 0, 500, 350)
        # no need to move the point of the geometry rect if you're going to use
        # the reference top left only
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width()
        y = 2 * ag.height() - sg.height() - widget.height()
        self.move(x, y)

    def center(self):
        self.resize(1400, 800)
        cent = QDesktopWidget().availableGeometry().center()  # Finds the center of the screen
        self.move(cent)
        self.frameGeometry().moveCenter(cent)


    ###################################################CAMERA SELECTION======================================================

    def returnHighlighted(self, param):
        print('The current highlighted index is: ', param)
        self.camThread.setCam(param)
        if self.vidConnectFlag == 1:
            self.camThread.stop()
            self.ClickStopVideo()

    ##########################################################################################################################

    # ===========================================PREDICTOR=========================================================


        #score = tf.nn.softmax(predictions[0])
        #class_names = ['Close', 'LForward', 'LTurn', 'Neutral', 'PointIn', 'PointOut', 'RForward', 'RTurn']
        #print(
           # "This image most likely belongs to {} with a {:.2f} percent confidence."
        #    .format(class_names[np.argmax(score)], 100 * np.max(score))
       # )


##############################################################################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    # win.show()
    sys.exit(app.exec())
