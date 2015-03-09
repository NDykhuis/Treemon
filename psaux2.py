'''
Created on Nov 16, 2010

@author: nathand
'''

import shlex, subprocess
from process2 import dprocess 
import time

class psaux(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.psaux = shlex.split("ps aux")

      
    # Union-y thing:
    # For all pids in data, inc using data from ps aux
    # Delete each pid from ps aux
    # For remaining pids, add them
        
    def gather(self, data, officialtime):
        pdata = {}
        psproc = subprocess.Popen(self.psaux, stdout=subprocess.PIPE)
        psproc.wait()
        pout = psproc.communicate()
        lines = pout[0].split('\n')
        for line in lines[1:]:   # should be for every lines
            if line == '': continue
            stats = line.split()
            stats[1] = int(stats[1])
            pdata[stats[1]] = (float(stats[2]), float(stats[3]), stats[9], stats[10]) # cpu, mem, cputime
            #if not stats[1] in data:
            #    data[stats[1]] = dprocess(stats[1], stats[10])
            #data[stats[1]].inc(float(stats[2]), float(stats[3]), stats[9], officialtime) 

        for pid, proc in data.iteritems():
            if pid in pdata:
                p = pdata.pop(pid)
                proc.inc({"cpu":p[0], "mem":p[1]}, officialtime)
                #proc.inc({"cpu":p[0], "mem":p[1], "cputime":p[2]}, officialtime)
                #proc.inc((p[0], p[1], p[2]), officialtime)
                #del pdata[pid]
            else:
                proc.alive = False
                proc.inc({"cpu":0.0, "mem":0.0}, officialtime)
                #proc.inc({"cpu":0.0, "mem":0.0, "cputime":0.0}, officialtime)
                #proc.inc((0,0,0), officialtime)

        for pid, p in pdata.iteritems():
            if p[3] == 'ps':    # Skip instances of running ps aux
                continue;
            data[pid] = dprocess(pid, p[3])
            data[pid].inc({"cpu":p[0], "mem":p[1]}, officialtime)
            #data[pid].inc({"cpu":p[0], "mem":p[1], "cputime":p[2]}, officialtime)

    