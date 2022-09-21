from collections import deque

from GActionHandler import GActionHandler, ActionSet


class Experiments():
    def gSignalHelper(self, m1: int, m2: int, m3: int):
        arr = [m1, m2, m3]
        return arr[self.gmode[0]]

    def __init__(self):
        super().__init__()
        ppath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
        print(ppath)
        #app = Application(backend="win32").start(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        #app = Application().connect(title='Google Chrome', timeout=10)
        #SendKeys('%{VK_TAB} 2')  # select all (Ctrl+A) and copy to clipboard (Ctrl+C)
        #app_dialog = app.top_window()
        #app_dialog.maximize()
        #app_dialog.set_focus()\

        self.gHist = deque([], maxlen=5)
        self.gHist.append('Neutral')
        self.gmode = deque([], maxlen=5)

        ##print(gHist)
        #self.tg = Gesture(1, 'LTurn' ,'e' , gHisdownt)tt
        ##print(self.tg.getHistory())4444444ttt
       # gHist.append('Dick')4down4
        #print(self.tg.getHistory())
        #gHist.append("Balls")4ttt
        #print(self.tg.getHistory()[0])444
        #str1= '{VK_NUMPAD4} 'tt
        #send_keys("{VK_LWIN}" "{VK_TAB}")ftttttttt
        #pyautogui.move(-2, 0)tt
        self.gmode.append(1)
        self.alf = ActionSet(['f'], ['t', 't'], ['down'])
        self.sRT = ActionSet(['win', 'tab'], ['win', 'tab'], ['space'])
        self.gaRT = GActionHandler([2, 2, 2], 'LTurn', self.alf, self.gHist, self.gmode)
        self.gaRT.sendAction()
        print(self.gHist)
        self.gaRT.sendAction()
        self.gHist.append('LTurn')
        self.gaRT.sendAction()
        self.gHist.append('LTurn')
        self.gaRT.sendAction()
        self.gHist.append('LTurn')
        self.gaRT.sendAction()
        self.gaRT.sendAction()
        print(self.gHist)
        print(self.gaRT.gesture)
        print(self.gaRT.History[-1] != self.gaRT.gesture )




if __name__ == '__main__':
    app = Experiments()
    # win.show()
    exit(0)