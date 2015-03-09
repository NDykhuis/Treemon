'''
Created on Nov 16, 2010

@author: nathand
'''

import time
import threading
from psaux2 import psaux 
import numpy
import process2

class datagather(threading.Thread):
    '''
    classdocs
    '''
    
    SHOW_IDLE = True
    INTERVAL = 1

    def __init__(self, data, dlock, plist):
        '''        Constructor        '''
        threading.Thread.__init__(self)
        self.init(data, dlock, plist)
      
    def init(self, data, dlock, plist):
        self.datc = {}
        self.datl = {}
        self.data = data
        self.dlock = dlock
        self.initted = True
        self.ticks = 0
        self.plist = plist
    
    def fauxrun(self):
        if not self.initted:
            raise RuntimeError("Datagather not initialized! (call init(data, dlock) first)")
        self.psaux = psaux()
        self.active = True
        self.interval = 1
        
    def run(self):
        print "RUNNED"
        if not self.initted:
            raise RuntimeError("Datagather not initialized! (call init(data, dlock) first)")
        self.psaux = psaux()
        self.active = True
        
        while (self.active):
            self.tick()
            for key in ("cpu", "mem"):
                self.niceval(key, 0, time.time()+1)
            time.sleep(self.INTERVAL)
        
    def tick(self):
        self.dlock.acquire()
        self.officialtime = time.time()  #time.clock()?
        #print "tick"
        self.ticks += 1
        
        self.psaux.gather(self.data, self.officialtime)
        self.updatepList()
        #lsof.gather()
        #some other thing.gather()
        
        # Temp Debug
        #self.printdata()
        
        self.dlock.release()
        
    def updatepList(self):
        self.plist.update_data(self.data)
        
    def ready(self):
        return self.ticks > process2.historysize/2
        
    def printdata(self):
        k = sorted(self.data.keys())
        for key in k:
            print key, self.data[key].cpu, self.data[key].mem 
        
    def niceval(self, val, mintime, maxtime):
        self.ltime = time.time()
        if val not in self.datc:
            self.datc[val] = {}
        self.datl[val] = self.datc[val]
        self.datc[val] = {}
        datl = []
        for pid, proc in self.data.iteritems():
            a = numpy.average(proc.data[val])
            if a!=0: 
                datl.append(a)
                self.datc[val][pid] = a

        idle = 100-sum(datl)
        if (idle > 0 and self.SHOW_IDLE): 
            datl.append(idle)
            self.datc[val][0] = idle

        datl = datl/sum(datl)
        return datl
    
    def valanim(self, val):
        # Interpolate between last and current tick
        ctime = time.time()
        frac = ctime - self.ltime
        omfrac = 1-frac
        dati = []
        pids = []
        for pid, dat in self.datc[val].iteritems():
            if pid in self.datl[val]:
                dati.append(frac*dat+omfrac*self.datl[val][pid])
                pids.append(pid)
            else:
                dati.append(frac*dat)
                pids.append(pid)
        # Sort lists by size (very unstable)
        #sorty = zip(dati, pids)
        #sorty.sort()
        #dati, pids = zip(*sorty)
        
        # Perform one run of bubble sort
        for i in range(len(dati)-1):
            if dati[i] < dati[i+1]:
                dati[i], dati[i+1] = dati[i+1], dati[i] 
                pids[i], pids[i+1] = pids[i+1], pids[i]
        return dati,pids
        pass
    
    def nicemem(self):
        pass
        
