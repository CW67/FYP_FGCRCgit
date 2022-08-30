from collections import deque
from pywinauto.keyboard import SendKeys
class Gesture():
    def __init__(self, mode, gesture, binding, history: deque):
        # mode, gesture, binding, history
        self.mode = mode
        self.binding = binding
        self.History = history
        self.gesture = gesture

        #Modes: 0- Default/function after neutral, 1: Continuos, 2: Function after any other gesture

    def getHistory(self):
        return self.History

    def sendAction(self):
        print('hi')
        if self.mode == 0 :
            SendKeys(self.binding)  # select all (Ctrl+A) and copy to clipboard (Ctrl+C)
        elif self.mode == 1:
            if self.History[0] == 'Neutral':
                SendKeys(self.binding)
        elif self.mode == 3:
            if self.History[0] != self.gesture:
                SendKeys(self.binding)
        else:
            print('Invalid mode')
