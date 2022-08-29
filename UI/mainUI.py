
from PyQt5.QtWidgets import *
import sys
from InputDialog import InputDialog
from SkinCalibrator import *
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QEventLoop, QTimer
from VideFunctions import VideoThread
from Predictor import *
from threading import Thread
import time



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
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        self.show()
        self.predictor = Predictor()

        self.sImg_shape = (480, 640, 3)
        self.sImg = np.empty(self.sImg_shape)

########################################################################################################################
#                                                   GUI Elements                                                            #
########################################################################################################################
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
        self.camThread.change_pixmap_signal.connect(self.update_image)

        # start the thread
        self.camThread.start()
        self.predictor.start()
        self.ss_video.clicked.connect(self.camThread.stop)  # Stop the video if button clicked
        self.ss_video.clicked.connect(self.ClickStopVideo)
        self.vidConnectFlag = 1



    # Activates when Start/Stop video button is clicked to Stop (ss_video)
    def ClickStopVideo(self):
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

    def MakePrediction(self):
        self.predictor.tdebug(self.sImg)

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
        self.hide()

    def showNoti(selfs):
        # import win10toast
        from win10toast import ToastNotifier
        # create an object to ToastNotifier class
        n = ToastNotifier()
        n.show_toast("GEEKSFORGEEKS", "You got notification", threaded=True)

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
