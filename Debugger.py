from datetime import datetime as dt
import time

class Debugger:
    __instance = None
    logs = []
    saveLogs = False
    def __new__(self):
        if self.__instance is None:
            self.__instance = super(Debugger,self).__new__(self)
        return self.__instance

    def throw(self, errorStr):
        logStr = dt.now().strftime('%H:%M:%S ') + errorStr
        self.logs.append(logStr)
        self.__react()

    def __react(self):
        print(self.logs[-1])

    def endSession(self):
        if len(self.logs) == 0:
            return
        self.throw('debug endSession')
        if not self.saveLogs:
            return
        date = dt.now().strftime('%d%m%y')
        time = dt.now().strftime('%H%M%S')
        with open('logs_' + date + '_' + time + '.txt', 'w') as file:
            for i in self.logs:
                file.write(i + '\n')

    def wait(self, waitTime):
        time.sleep(waitTime/1000)



