'''
Created on Nov 23, 2010

@author: nathand
'''
import time
import gtk
import cairo
import numpy
import threading
import splittreemap
import gobject
import datagather2
import process2
import math

class tmrender(threading.Thread):
    '''
    classdocs
    '''
    active = False
    
    selected_pid = -1

    def __init__(self,dgather,dlock,drawarea, val):
        '''        Constructor        '''
        threading.Thread.__init__(self)
        self.dgather = dgather
        self.dlock = dlock
        self.drawarea = drawarea
        self.active = True
        self.sdraw = splittreemap.splittreemap([])
        self.cr = drawarea.window.cairo_create()
        self.width, self.height = drawarea.window.get_size()
        #self.cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.cr.set_font_size(12)
        x_bearing, y_bearing, width, self.theight = self.cr.text_extents("1")[:4]
        self.rects = []
        self.val = val
            
    def run(self):
        
        #gobject.timeout_add(500, self.paintTreemaps(self.cr, self.width, self.height))
        
        while self.active:
            self.paintTreemaps(self.cr, self.width, self.height)
            time.sleep(2)
    
    def update(self, t1=0, t2=0, t3=0):
        self.cr = self.drawarea.window.cairo_create()
        #self.cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.cr.set_font_size(12)
        self.width, self.height = self.drawarea.window.get_size()
        
        
    def getclick(self, x, y):
        for r in self.rects:
            # check if this point is within the rectangle
            if (x-r.x)*(x-r.x-r.w) < 0 and (y-r.y)*(y-r.y-r.h) < 0:
                #print x, r.x, r.w
                #print y, r.y, r.h
                return r.id
        return 0
        
    def paintTreemaps(self):
        #self.dgather.tick()
        cr = self.cr
        
        # 1: red/green  2: brightness  3: normal
        colorcalc = 3
        
        #print "drawing"
        self.dlock.acquire()
        
        # Check if data is ready:
        if not self.dgather.ready():
            cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
            cr.move_to(5, 5+self.theight)
            cr.show_text("Gathering...")
            self.dlock.release()
            self.notready = True
            return self.active
        else:
            self.notready = False
        
        # put the data all into nice format
        #items = self.dgather.nicecpu(0, self.dgather.officialtime)
        #items, pids = self.dgather.cpuanim()
        items, pids = self.dgather.valanim(self.val)
        #items = (0.5, 0.25, 0.125, 0.125)
        # call the painter on each category
        self.rects = self.sdraw.layout(0, 0, self.width, self.height, items, pids)
        if not self.rects:
            self.dlock.release()
            return True
        for r in self.rects:
            #print r.x, r.y, r.w, r.h
            pid = r.id
            # Get comparison of data usage
            if pid != 0 and colorcalc != 3:
                proc = self.dgather.data[pid]
                piddata = proc.getrow()
                if self.val == 'cpu': pidavg = piddata[2]
                else: pidavg = piddata[3]
                pidlast = proc.data[self.val][proc.lasttime%process2.historysize]
                pd = (pidlast - pidavg)/2.0  # -45 to 45
                #pd /= 45    # -1 to 1
                #pd = math.sqrt(math.sqrt(abs(pd)))  # Make more extreme
                #pd *= 45
                #if pidlast < pidavg: pd = -pd
                #else: pd = 0
                if colorcalc != 3:
                    if pd > 0: pd+=1; s = 1 
                    else: pd -= 1; s = -1
                    pd = s*pd*pd
                    #pd = 10*pd
                    if pd > 35: pd = 35
                    elif pd < -35: pd = -35
            else:
                pd = 0
            if colorcalc == 3:
                rd = (pid % 235 + 20)/255.0
                g = ((pid*pid) % 235 + 20)/255.0
                b = ((pid*pid*pid) % 235 + 20)/255.0
            elif colorcalc == 1:
                rd = ((-pd/35)*128+128)/255.0
                g = ((pd/35)*128+128)/255.0
                b = 0.5
            elif colorcalc == 2:
                pd += 20
                rd = (pid % (255-55)+pd)/255.0
                g = ((pid*pid) % (255-55)+pd)/255.0
                b = ((pid*pid*pid) % (255-55)+pd)/255.0
            #extracolor=120
            #rrand = numpy.random.randint(extracolor - 40)
            #grand = numpy.random.randint(extracolor - rrand)
            #brand = numpy.random.randint(extracolor - rrand - grand)
            #rd = (pid % (255-rrand)+rrand)/255.0
            #g = ((pid*pid) % (225-grand)+grand)/255.0
            #b = ((pid*pid*pid) % (225-brand)+brand)/255.0
            #rd = numpy.random.random()
            #g = numpy.random.random()
            #b = numpy.random.random()
            cr.set_source_rgb(rd, g, b)
            cr.rectangle(r.x, r.y, r.w, r.h)
            if pid == self.selected_pid:
                cr.fill_preserve()
                cr.set_line_width(3.0)
                cr.set_source_rgb(1.0, 0.0, 0.0)
                cr.stroke()
            else:
                cr.fill()
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cr.move_to(r.x, r.y+self.theight)
            cr.show_text(str(pid))
        self.dlock.release()
        #self.cpuarea.queue_draw()
        
        return self.active
