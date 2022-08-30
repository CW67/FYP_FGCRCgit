from collections import deque
from pywinauto.keyboard import send_keys
import pyautogui
import time

import time
class Gesture():
    def __init__(self, mode, gesture, binding, history: deque ):
        # mode, gesture, binding, history
        self.mode = mode
        self.binding = binding
        self.History = history
        self.gesture = gesture
        self.holdKey = False
        self.holdMouse = False

        #Modes: 0- Default/function after neutral, 1: Continuos, 2: Function after any other gesture

    def getHistory(self):
        return self.History

    def holdKeyWatcher(self):
        while True:
            if self.History[-1] != self.gesture:
                self.holdKey = False
                up_bind = self.binding + " up}"
                send_keys(up_bind)
                break
            time.sleep(0.05)

    def holdMouseWatcher(self):
        while True:
            if self.History[4] != self.gesture:
                self.holdMouse = False
                break
            pyautogui.move(-4, 0)

    def sendAction(self):
        print('hi')
        if self.mode == 0 :
            send_keys(self.binding)  #Perform regardless (will continuosly send)

        elif self.mode == 1:
            if self.History[-1] == 'Neutral': #Perform once (send only after neutral)
                send_keys(self.binding)

        elif self.mode == 3:
            if self.History[-1] != self.gesture: #Perform once (send after any other gesture)
                send_keys(self.binding)

        elif self.mode == 4 and self.holdKey == False:
            pyautogui.keyDown(num4)
            self.holdKey = True
            self.holdMouse = False
            self.holdKeyWatcher()

     #================pyautogui mouse movement=============
        elif self.mode == 'ml':
            pyautogui.move(-15, 0)

        elif self.mode == 'mr':
            pyautogui.move(15, 0)

        elif self.mode == 'mu':
            pyautogui.move(0, 15)

        elif self.mode == 'md':
            pyautogui.move(0, -15)

        elif self.mode == 'mc':
            if self.History[4] == 'Neutral':
                pyautogui.click()


        else:
            print('Invalid mode')
