from collections import deque
from numpy import *

historysize = 10

class dp:
    cpu = 0
    mem = 0
    def __init__(self, cpu, mem):
        self.cpu = cpu; self.mem = mem

class dprocess:
    def __init__(self, pid, command):
        self.pid = pid; self.command = command
        self.starttime = 0
        self.lasttime = 0
        self.datah = {}; self.cputime = 0
        self.data = {}
        self.alive = True
        # for python 2.7, set maxlen of cpu and mem
    
    def changeHsize(self, newsize):
        time = self.lasttime
        self.newdata = zeros(newsize)
        for _ in reversed(range(min(newsize, historysize))):
            self.newdata[newsize % time] = self.data[historysize % time]
            time -= 1 
        self.newdata = zeros(newsize)
        self.data = self.newdata
        historysize = newsize 
    
    def incpsaux(self, cpu, mem, time):
        time = int(time)
        
    def getvar(self, var):
        return self.data[var]
    
    def getrow(self):
        #return (self.pid, self.command, self.data['cpu'][self.lasttime%historysize], self.data['mem'][self.lasttime%historysize])
        return (self.pid, self.command, average(self.data['cpu']), average(self.data['mem']))
        
    def inc(self, datadict, time):
        time = int(time)
        for key, val in datadict.iteritems():
            if key not in self.data:
                self.data[key] = zeros(historysize)
            self.data[key][time % historysize] = val
        self.lasttime = time
    
    def incblank(self, time):
        time = int(time)
        self.data[time % historysize] = (0,0,0,0)
        self.active = False
        if time - self.lasttime > historysize:
            return 0
        else: return 1

class sprocess:
    def __init__(self):
        self.pid = 0
        self.cpu = 0
        self.mem = 0
        