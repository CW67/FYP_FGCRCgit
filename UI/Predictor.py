from threading import Thread
import tensorflow as tf
from tensorflow import keras
from numpy import expand_dims
from keras.utils import img_to_array
from keras.models import load_model
from plyer import notification
from GestureHandler import GestureHandler, ActionSet
import numpy as np
import cv2
import time
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal, QTimer)
from collections import deque


class Predictor(QThread):
    def __init__(self, msg: deque, mode_s: deque):
        super().__init__()

        # Message used to send name of  gesture detected back to main UI
        self.msg = msg
        self.mode_s = mode_s
        # Load the saved settings from segmentation calibration
        vals = []
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

        # Load the prediction model
        self.fmodel = keras.models.load_model('newmod4.h5', compile=False)
        self._run_flag = True
        self.sImg_shape = (480, 640, 3)
        self.sImg = np.empty(self.sImg_shape)
        self.all_zeros = not np.any(self.sImg)

        # gHist stores history of last 5 predicted gestures
        self.gHist = deque([], maxlen=5)

        # initialize gesture names
        self.class_names = ['Close', 'LForward', 'LTurn', 'Neutral', 'PointIn', 'PointOut', 'RForward', 'RTurn']
        self.statusMessage = "None"

        # Gesture sett variable
        self.gmode = deque([], maxlen=1)
        self.gmode.append(0)

        # Action sets help to appoint mutiple actions to one gesture
        # (maximum of 2 inputs per slot: hold first, press 2nd, then release first)
        self.sRF = ActionSet(['mu'], ['su'], ['up'])
        self.sLF = ActionSet(['md'], ['sd'], ['down'])
        self.sRT = ActionSet(['mr'], ['ctrl', 'tab'], ['right'])
        self.sLT = ActionSet(['ml'], ['ctrl', 'pgup'], ['left'])
        self.sPO = ActionSet(['win', 'tab'], ['ctrleft', 't'], ['k'])
        self.sPI = ActionSet(['mc'], [''], ['f'])

        # Gesture type slot 1: md = mouse down, ml = mouse left, mu = mouse up, mc = mouse click, mr = mouse right
        # slot 1: 1 = send signal whenever received, 2: send only if previous gesture is neutral,
        # 3 = send if previuos gesture is different , 4: unimplemented
        # Slot 2: name of gesture being sent
        # Slot 3: Set of gestures (using actionSet object)
        # 1 element = perform that keystroke, 2 elements = hold first, press second, then release first
        # Slot 4: Gesture history queue for implementing slot 1 methodstt

        self.gaRF = GestureHandler([0,0,0], 'RForward', self.sRF, self.gHist, self.gmode)
        self.gaLF = GestureHandler([0,0,0], 'LForward', self.sLF, self.gHist, self.gmode)
        self.gaRT = GestureHandler([0,2,0], 'RTurn', self.sRT, self.gHist, self.gmode)
        self.gaLT = GestureHandler([0,2,0], 'LTurn', self.sLT, self.gHist, self.gmode)
        self.gaPO = GestureHandler([2,2,2], 'PointOut', self.sPO, self.gHist, self.gmode)
        self.gaPI = GestureHandler([2,2,2], 'PointIn', self.sPI, self.gHist, self.gmode)

        # self.gn = GestureHandler(, 'Neutral', [], self.gHist)
        # self.gs = GestureHandler(, 'Close', [], self.gHist)

        # print(self.all_zeros)
        self._events = {}

    # =======================Helper Function for gesture signal siwtching between modes
    # Example, gSignalHelper (1,1,2) returns 1 when mode is set to 0 or 1, and 2 if mode is set to 3
    # used for cases where gestures requires different signal send types between different modes
    def gSignalHelper(self, m1: int, m2: int, m3: int):
        arr = [m1, m2, m3]

        return arr[self.gmode[0]]

    # =======================Functions to dispatch event to main UI===============================
    def addEventListener(self, name, func):
        if name not in self._events:
            self._events[name] = [func]
        else:
            self._events[name].append(func)

    def dispatchEvent(self, name):
        functions = self._events.get(name, [])
        for func in functions:
            QTimer.singleShot(0, func)

    # ===========================Functino to update the image loaded in the predictor from the main UI================
    def updateImg(self, image):
        self.sImg = image
        # print(self.sImg.shape)
        self.all_zeros = not np.any(self.sImg)

    # def ExecuteGesture(self, ):
    # def onPred(self):

    # -===========================Method too checkk all history items foor long hold gestures====================
    def all_same(self):
        return all(x == self.gHist[0] for x in self.gHist)

    # ===========================================Run method============================================
    def run(self):
        self._run_flag = True
        vals = []
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

        self._close_flag = True
        self.pNeutralFlag = 0
        count = 0
        self.gHist.append('Neutral')
        while self._run_flag:
            # time.sleep(0.3)
            if self.all_zeros:
                print('Predictor not running: no image detected')
                self.msg.append('nothing happening')
                self.dispatchEvent('Hello')
            else:
                prediction = self.predict_rgb(self.sImg)
                # elif self.PNeutralFlag == 1 and gHist[0] == prediction and gHist[0] == gHist[1] :
                if prediction == 'Neutral':
                    self._close_flag = True
                    print('Gesture set to neutral, mmode is')
                    print(self.gmode[0])
                    self.gHist.append(prediction)
                if prediction == 'Close' :
                    self.gHist.append(prediction)
                    if self.all_same() and self._close_flag:
                        self._close_flag = False
                        if self.gmode[0] < 2:
                            toReplace = int(self.gmode[0] + 1)
                            self.gmode.append(toReplace)
                            self.mode_s.append(self.gmode[0])
                            print('Closing, moving to next')
                            print(self.gmode[0])
                            self.dispatchEvent('col change')
                        else:
                            toReplace = 0
                            self.gmode.append(toReplace)
                            self.mode_s.append(self.gmode[0])
                            print(self.gmode[0])
                            print('Closing, reset t 0')
                            self.dispatchEvent('col change')
                if prediction == 'LForward':
                    self.gaLF.sendAction()
                    print('Performing LForward Action')
                if prediction == 'LTurn':
                    self.gaLT.sendAction()
                    print('Performing LTurn Action')
                if prediction == 'RForward':
                    self.gaRF.sendAction()
                    print('Performing RFoward Action')
                if prediction == 'RTurn':
                    self.gaRT.sendAction()
                    print('Performing RTurn Action')
                if prediction == 'PointIn':
                    self.gaPI.sendAction()
                    print('Performing PointIn Action')
                if prediction == 'PointOut':
                    self.gaPO.sendAction()
                    print('Performing PointOut Action')
                if prediction == 'fail':
                    print('Failed too recognize gesture')

                msgstr = 'performing' + prediction
                self.msg.append(msgstr)
                self.dispatchEvent('Hello')

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.sImg = np.empty(self.sImg_shape)

    # =============================Function to apply pre-processing to the collected image and perform prediction=============
    def predict_rgb(self, image):
        width = 64
        height = 64
        dim = (width, height)
        lower = np.array([self.hLow, self.sLow, self.vLow], dtype="uint8")
        upper = np.array([self.hHigh, self.sHigh, self.vHigh], dtype="uint8")

        # image = np.array(image, dtype='float32')
        # image /= 255
        image = image.astype(np.uint8)
        converted = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        # Generate Binary Skin Mask
        skinMask = cv2.inRange(converted, lower, upper)
        skinMask = skinMask.astype("uint8")

        # apply a series of erosions and dilations to the mask
        # using an elliptical kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skinMask = cv2.erode(skinMask, kernel, iterations=3)
        skinMask = cv2.dilate(skinMask, kernel, iterations=5)
        skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
        skinMask = cv2.resize(skinMask, dim)

        bin_img = cv2.cvtColor(skinMask, cv2.COLOR_GRAY2RGB)
        # print(bin_img.shape)
        img_array = keras.utils.img_to_array(bin_img)
        img_array = expand_dims(img_array, 0)
        predictions = self.fmodel.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        # print(
        # "This image most likely belongs to {} with a {:.2f} percent confidence."
        #   .format(class_names[np.argmax(score)], 100 * np.max(score))
        # )
        score = float("%0.2f" % (max(score) * 100))
        result = self.class_names[np.argmax(predictions)]
        # print(result)
        # print(score)

        if score > 70:
            return result
        else:
            return 'fail'

    def tdebug(self, image):
        width = 64
        height = 64
        dim = (width, height)
        lower = np.array([self.hLow, self.sLow, self.vLow], dtype="uint8")
        upper = np.array([self.hHigh, self.sHigh, self.vHigh], dtype="uint8")

        # image = np.array(image, dtype='float32')
        # image /= 255
        image = image.astype(np.uint8)

        converted = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        # Generate Binary Skin Mask
        skinMask = cv2.inRange(converted, lower, upper)
        skinMask = skinMask.astype("uint8")

        # apply a series of erosions and dilations to the mask
        # using an elliptical kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skinMask = cv2.erode(skinMask, kernel, iterations=3)
        skinMask = cv2.dilate(skinMask, kernel, iterations=5)
        skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
        skinMask = cv2.resize(skinMask, dim)

        bin_img = cv2.cvtColor(skinMask, cv2.COLOR_GRAY2RGB)

        cv2.imshow("skinMask", bin_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # (bin_img.shape)
        img_array = keras.utils.img_to_array(bin_img)
        img_array = expand_dims(img_array, 0)
