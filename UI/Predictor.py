from threading import Thread
import tensorflow as tf
from tensorflow import keras
from numpy import expand_dims
from keras.utils import img_to_array
from keras.models import load_model
from plyer import notification
import numpy as np
import cv2
import time
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)
from collections import deque

class Predictor(QThread):
    def __init__(self):
        super().__init__()
        vals = []
        gStor = []
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

        self.fmodel = keras.models.load_model('newmod.h5', compile=False)
        self._run_flag = True
        self.sImg_shape = (480, 640, 3)
        self.sImg = np.empty(self.sImg_shape)
        self.all_zeros = not np.any(self.sImg)
        self.pNeutralFlag = 0
        print(self.all_zeros)


    def updateImg(self, image):
        self.sImg = image
        #print(self.sImg.shape)
        self.all_zeros = not np.any(self.sImg)

    def run(self):
        self._run_flag = True
        count = 0
        gHist = deque([], maxlen=10)
        while self._run_flag:
            time.sleep(0.2)
            if self.all_zeros:
                print('Predictor not running: no image detected')
            else:
                prediction = self.predict_rgb(self.sImg)
                gHist.append([prediction])
                #elif self.PNeutralFlag == 1 and gHist[0] == prediction and gHist[0] == gHist[1] :
                if prediction == 'Neutral':
                    self.pNeutralFlag = 1
                    print('Gesture set to neutral')
                if prediction == 'Close':
                    self.pNeutralFlag = 0
                    print('Performing Close Action')
                if prediction == 'LForward':
                    self.pNeutralFlag = 0
                    print('Performing LForward Action')
                if prediction == 'LTurn':
                    self.pNeutralFlag = 0
                    print('Performing LTurn Action')
                if prediction == 'RForward':
                    self.pNeutralFlag = 0
                if prediction == 'RTurn':
                    self.pNeutralFlag = 0
                if prediction == 'PointIn':
                    self.pNeutralFlag = 0
                if prediction == 'PointOut':
                    self.pNeutralFlag = 0
                    print('Performing PointOut Action')




    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.sImg = np.empty(self.sImg_shape)
        self.all_zeros = not np.any(self.sImg)
        self._run_flag = False


    def predict_rgb(self, image):
        width = 64
        height = 64
        dim = (width, height)
        lower = np.array([self.hLow, self.sLow, self.vLow], dtype="uint8")
        upper = np.array([self.hHigh, self.sHigh, self.vHigh], dtype="uint8")

        # image = np.array(image, dtype='float32')
        # image /= 255

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
        print(bin_img.shape)
        img_array = keras.utils.img_to_array(bin_img)
        img_array = expand_dims(img_array, 0)
        predictions = self.fmodel.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        class_names = ['Close', 'LForward', 'LTurn', 'Neutral', 'PointIn', 'PointOut', 'RForward', 'RTurn']
        #print(
         #"This image most likely belongs to {} with a {:.2f} percent confidence."
         #   .format(class_names[np.argmax(score)], 100 * np.max(score))
        #)
        score = float("%0.2f" % (max(score) * 100))
        result = class_names[np.argmax(predictions)]
        print(result)
        print(score)

        if score > 50:
            return result
        else:
            return 'neutral'

    def tdebug(self , image):
        width = 64
        height = 64
        dim = (width, height)
        lower = np.array([self.hLow, self.sLow, self.vLow], dtype="uint8")
        upper = np.array([self.hHigh, self.sHigh, self.vHigh], dtype="uint8")

        # image = np.array(image, dtype='float32')
        # image /= 255

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

        print(bin_img.shape)
        img_array = keras.utils.img_to_array(bin_img)
        img_array = expand_dims(img_array, 0)

