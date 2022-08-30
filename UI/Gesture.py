from collections import deque
from pywinauto.keyboard import send_keys
import time
class Gesture():
    def __init__(self, mode, gesture, binding, history: deque):
        # mode, gesture, binding, history
        self.mode = mode
        self.binding = binding
        self.History = history
        self.gesture = gesture
        self.hold = False

        #Modes: 0- Default/function after neutral, 1: Continuos, 2: Function after any other gesture

    def getHistory(self):
        return self.History

    def sendAction(self):
        print('hi')
        if self.mode == 0 :
            send_keys(self.binding)  # select all (Ctrl+A) and copy to clipboard (Ctrl+C)
            self.hold = False
        elif self.mode == 1:
            if self.History[-1] == 'Neutral':
                send_keys(self.binding)
                self.hold = False
        elif self.mode == 3:
            if self.History[-1] != self.gesture:
                send_keys(self.binding)
                self.hold = False
        elif self.mode == 4  and self.hold == False:
            send_keys(self.binding)
            self.hold = True

        else:
            print('Invalid mode')
