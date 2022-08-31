from collections import deque
from pywinauto.keyboard import send_keys
import pyautogui
import time
from typing import List

import time


#Defines the set of actions a GestureHandler will perform, 3 sets, of 2 each
class ActionSet():
    def __init__(self, binding1: List[str], binding2: List[str], binding3: List[str]):
        self.bindList = [binding1, binding2, binding3]

    def getSet(self, index):
        if index <=2:
            print(self.bindList[index])
            return self.bindList[index]
        return []

#Class which handles performing key / mouse send inputs
class GestureHandler():
    def __init__(self, mode, gesture, binding: ActionSet, history: deque , gesture_mode):
        # mode, gesture, binding, history
        self.mode = mode
        self.binding = binding
        self.History = history
        self.gesture = gesture
        self.holdKey = False
        self.holdMouse = False
        self.gmode = gesture_mode

        #Modes: 0- Default/function after neutral, 1: Continuos, 2: Function after any other gesture

    def getHistory(self):
        return self.History

    def keysend_helper(self):
        sendSet = self.binding.getSet(self.gmode)
        if len(sendSet) == 2:
            pyautogui.keyDown(sendSet[0])
            time.sleep(.1)
            pyautogui.press(sendSet[1])
            time.sleep(.1)
            pyautogui.keyUp(sendSet[0])

        elif len(sendSet) == 1:
            if sendSet[0] == 'ml':
                pyautogui.move(-15, 0)

            elif sendSet[0] == 'mr':
                pyautogui.move(15, 0)

            elif sendSet[0] == 'mu':
                pyautogui.move(0, -15)

            elif sendSet[0] == 'md':
                pyautogui.move(0, 15)

            elif sendSet[0] == 'mc':
                pyautogui.click()

            elif sendSet[0] == 'su':
                pyautogui.scroll(10)

            elif sendSet[0] == 'sd':
                pyautogui.scroll(-5)
            else:
                pyautogui.press(sendSet[0])


    def holdKeyWatcher(self):
        while True:
            if self.History[-1] != self.gesture:
                self.holdKey = False
                up_bind = self.binding + " up}"
                send_keys(up_bind)
                break
            time.sleep(0.05)

    def sendAction(self):
        if self.mode == 0 :
            self.keysend_helper()  #Perform regardless (will continuosly send)

        elif self.mode == 1:
            if self.History[-1] == 'Neutral': #Perform once (send only after neutral)
                self.keysend_helper()

        elif self.mode == 2:
            if self.History[-1] != self.gesture: #Perform once (send after any other gesture)
                self.keysend_helper()

     #================pyautogui mouse movement=============
        else:
            print('Invalid mode')
