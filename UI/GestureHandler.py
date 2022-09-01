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
            return self.bindList[index]
        return []

#Class which handles performing key / mouse send inputs
class GestureHandler():
    def __init__(self, mode, gesture, binding: ActionSet, history: deque , gesture_mode: deque):
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
        print('FROM GESTURE HANDLER')
        print(self.gmode[0])
        sendSet = self.binding.getSet(self.gmode[0])
        if len(sendSet) == 2:
            pyautogui.hotkey(sendSet[0], sendSet[1])
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
                pyautogui.scroll(25)

            elif sendSet[0] == 'sd':
                pyautogui.scroll(-25)
            else:
                pyautogui.press(sendSet[0])
        self.History.append(self.gesture)


    def holdKeyWatcher(self):
        while True:
            if self.History[-1] != self.gesture:
                self.holdKey = False
                up_bind = self.binding + " up}"
                send_keys(up_bind)
                break
            time.sleep(0.05)

    def sendAction(self):
        print('MODE')
        amode = int(self.mode[self.gmode[0]])
        print(amode)
        print(self.History[-1])
        print(amode == 1)
        if amode == 0:
            self.keysend_helper()  #Perform regardless (will continuosly send)
        elif amode == 1 and self.History[-1] == 'Neutral':
            print('PERFORMING MODE 1')
            self.keysend_helper()
        elif amode == 2 and self.History[-1] != self.gesture:
            print('PERFORMING MODE 2')
            print(self.History)
            print(self.History[-1] != self.gesture)
            print(self.mode == 2)
            self.keysend_helper()
            time.sleep(1)
     #================pyautogui mouse movement=============
        else:
            print('Invalid mode')
        return self.gesture
