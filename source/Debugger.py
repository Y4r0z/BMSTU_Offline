from datetime import datetime as dt
import time

class Debugger:
    __instance = None
    logs = []
    saveLogs = False
    def __new__(self):
        if self.__instance is None:
            self.__instance = super(Debugger,self).__new__(self)
            self.timer = Timer()
        return self.__instance

    def throw(self, errorStr):
        logStr = dt.now().strftime('%H:%M:%S ') + str(errorStr)
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


class Timer:
    def __init__(self):
        self.timer = 0
        self.log = []
        self.waypoints = 0
    
    def start(self):
        self.timer = time.time()
        self.waypoints = 0
    
    def clk(self, name = None):
        result = round((time.time() - self.timer)*1000,2)
        self.log.append(result)
        if name is None:
            Debugger().throw("Timer clk(" + str(self.waypoints) + "): " + str(result) + " ms.")
        else:
            Debugger().throw("Timer clk(" + name + "): " + str(result) + " ms.")
        self.timer = time.time()
        self.waypoints+=1

    def stop(self):
        result = round((time.time() - self.timer)*1000,2)
        self.log.append(result)
        Debugger().throw("Timer: " + str(result) + " ms.")
    
    def printLog(self):
        for i in self.log:
            print("Timer: " + str(i) + " ms.")



