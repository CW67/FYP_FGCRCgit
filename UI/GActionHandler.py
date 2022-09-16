from collections import deque
from pywinauto.keyboard import send_keys
import pyautogui
from typing import List
import time
#Author: Cheong Fulian, William
#Description: Contains classes that handles all methods related to gesture keybinds or mouse emulation

# Container for the the set of actions a GActionHandler will perform
# Contains 3 sets of 'gesture action' arrays, supports either single or combination of 2 keys
class ActionSet():
    def __init__(self, binding1: List[str], binding2: List[str], binding3: List[str]):
        self.bindList = [binding1, binding2, binding3]

    def getSet(self, index):
        if index <=2:
            return self.bindList[index]
        return []

#Class which handles performing the key press and their behaviour
class GActionHandler():
    def __init__(self, mode, gesture, binding: ActionSet, history: deque , gesture_mode: deque):
        # mode, gesture, binding, history
        self.gesture_modes = mode #Array consisting of 3 gesture modes for the 3 different set of actions assigned
        self.binding = binding #The set of actions for the gesture
        self.History = history #History deque synced with Predictor
        self.gesture = gesture #The gesture assigned to this gesture object
        self.holdKey = False
        self.holdMouse = False
        self.active_mode = gesture_mode #Current active gesture mode

        #Modes: 0- Default/function after neutral, 1: Continuos, 2: Function after any other gesture

    #Retrieve gesture history(deque from predictor)
    def getHistory(self):
        return self.History

    #Class that actually sends the key send or mouse movemennt
    def keysend_helper(self):
        print('FROM GESTURE HANDLER')
        print(self.active_mode[0])
        sendSet = self.binding.getSet(self.active_mode[0])
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

    #Controls the behaviour of the key press. Being hold continuos or single tap
    def sendAction(self):
        print('MODE')
        amode = int(self.gesture_modes[self.active_mode[0]]) #Set the action/keybind to use from gesture_modes based on current active mode
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
            print(self.gesture_modes == 2)
            self.keysend_helper()
            time.sleep(1)
     #================pyautogui mouse movement=============
        else:
            print('Invalid mode')
        return self.gesture
