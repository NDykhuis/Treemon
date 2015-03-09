'''
Created on Nov 16, 2010

@author: nathand
'''

import pygtk
pygtk.require('2.0')
import gtk, gobject

from datagather2 import datagather
from tmrender import tmrender
import threading
import splittreemap
import numpy
import time
import gtk.gdk

handle_id = None

import proclist


class treemon():
    '''    The main Treemap Monitor window    '''
    # Class member variables:
    # window - GTK window
    # cpuarea, memarea, diskarea, netarea

    uistring = '''
    <ui>
      <menubar name="MenuBar">
        <menu action="File">
          <menuitem action="Options" />
          <menuitem action="Quit" />
        </menu>
      </menubar>
    </ui>'''

    selected_pid = -1

    def __init__(self):
        '''        Constructor        '''
        gtk.gdk.threads_init()
        
        self.initGTKWindow()
        self.initGTKobjects()
        
    def start(self):
        
        self.data = {}
        self.dlock = threading.Lock()
        self.initDataThread()
        self.window.show_all()
        self.initRenderer()
        self.runGTK()
        
    def stop(self, extraarg1=0, extraarg2=0):
        self.dgather.active = False
        self.cpurender.active = False
        self.memrender.active = False
        self.dgather.join(1)
        #self.tmrender.join(1)
        gtk.main_quit()
        
    def initGTKWindow(self):
        self.window = gtk.Window()
        self.window.connect("destroy", self.stop)
        self.window.set_default_size(800, 600)
    
    def print_hello(self, thing1=0, thing2=0):
        print "hello!"
        
    def menuInit(self):
        uimanager = gtk.UIManager()
        
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        actiongroup = gtk.ActionGroup('UIManagerExample')
        self.actiongroup = actiongroup

        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Quit', None,
              'Quit the Program', self.stop),
              ('Options', None, '_Options', None,
              'Set program options', self.print_hello),
               ('File', None, '_File')])
        uimanager.insert_action_group(actiongroup, 0)
        
        #merge_id = uimanager.add_ui_from_file("ui.xml")
        merge_id = uimanager.add_ui_from_string(self.uistring)
        print merge_id
        print uimanager.get_widget('/MenuBar')
        return uimanager.get_widget('/MenuBar')

    def oldMenuInit(self):
        accel_group = gtk.AccelGroup()
        
        
        self.menu_items = (
           ( "/_File",         None,         None, 0, "<Branch>" ),
           ( "/File/_New",     "<control>N", self.print_hello, 0, None ),
           ( "/File/_Open",    "<control>O", self.print_hello, 0, None ),
           ( "/File/_Save",    "<control>S", self.print_hello, 0, None ),
           ( "/File/Save _As", None,         None, 0, None ),
           ( "/File/sep1",     None,         None, 0, "<Separator>" ),
           ( "/File/Quit",     "<control>Q", self.stop, 0, None ),
           ( "/_Options",      None,         None, 0, "<Branch>" ),
           ( "/Options/Test",  None,         None, 0, None ),
           ( "/_Help",         None,         None, 0, "<LastBranch>" ),
           ( "/_Help/About",   None,         None, 0, None ),
           )
        
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(self.menu_items)
        self.window.add_accel_group(accel_group)
        self.item_factory = item_factory

        return item_factory.get_widget("<main>")


    def initGTKobjects(self):
        vbox = gtk.VBox()
        self.window.add(vbox)
        
        
        menubar = self.menuInit()
        vbox.pack_start(menubar, False)

        
        #hbox = gtk.HBox()
        hpanes = gtk.HPaned()
        
        cpubox = gtk.Frame("CPU")
        membox = gtk.Frame("MEM")
        diskbox = gtk.AspectFrame("DISK")
        netbox = gtk.AspectFrame("NET")
        
        #treebox = gtk.VBox()
        self.pl = proclist.proclist(self.window)
        treebox = self.pl.getWidget() 
        
        montable = gtk.Table(rows=2, columns=2, homogeneous = True)
        montable.attach(cpubox, 0, 1, 0, 1)
        montable.attach(membox, 1, 2, 0, 1)
        montable.attach(diskbox, 0, 1, 1, 2)
        montable.attach(netbox, 1, 2, 1, 2)
        montable.set_size_request(400,400)
        
        #hbox.pack_start(montable)
        #hbox.pack_start(treebox)
        hpanes.add1(montable)
        hpanes.add2(treebox)
        vbox.pack_start(hpanes)
        
        self.cpuarea = gtk.DrawingArea()
        #self.cpuarea.set_size_request(100,100)
        #vbox.pack_start(self.cpuarea)
        cpubox.add(self.cpuarea)
        
        self.memarea = gtk.DrawingArea()
        membox.add(self.memarea)
        
        #data_button = gtk.Button("DATA!")
        #data_button.connect("clicked", self.on_data_clicked, self.cpuarea)
        #vbox.pack_start(data_button, expand=False)
        pause_button = gtk.Button("Pause")
        pause_button.connect("clicked", self.on_pause_clicked)
        vbox.pack_start(pause_button, expand=False)
        
    def initRenderer(self):
        self.cpurender = tmrender(self.dgather, self.dlock, self.cpuarea, 'cpu')
        self.cpuarea.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.cpuarea.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.cpuarea.connect("button_press_event", self.on_tm_clicked)
        self.cpuarea.connect("button_release_event", self.on_tm_clicked)
        self.cpuarea.connect("configure_event", self.cpurender.update)
        
        self.memrender = tmrender(self.dgather, self.dlock, self.memarea, 'mem')
        self.memarea.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.memarea.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.memarea.connect("button_press_event", self.on_tm_clicked)
        self.memarea.connect("button_release_event", self.on_tm_clicked)
        self.memarea.connect("configure_event", self.memrender.update)
        
        gobject.timeout_add(300, self.cpurender.paintTreemaps)
        gobject.timeout_add(300, self.memrender.paintTreemaps)
        
        
    def handler(self, widget, event):
        pass
        
    def on_data_clicked(self, button, area):
        #self.paintTreemaps()
        gobject.timeout_add(300, self.cpurender.paintTreemaps)
        gobject.timeout_add(300, self.memrender.paintTreemaps)
        #self.cpuarea.queue_draw()
        #self.tmrender.start()
        #gobject.timeout_add(500, self.paintTreemaps)
        
    def on_pause_clicked(self,button):
        self.cpurender.active = not self.cpurender.active 
        self.memrender.active = not self.memrender.active
        if self.cpurender.active == True:
            gobject.timeout_add(300, self.cpurender.paintTreemaps)
        if self.memrender.active == True:
            gobject.timeout_add(300, self.memrender.paintTreemaps)
    
    def on_tm_clicked(self, widget, event, callback_data=None):
        #if widget == self.cpuarea
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.startx = event.x; self.starty = event.y
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            if widget == self.cpuarea:
                pid = self.cpurender.getclick(self.startx, self.starty)
            elif widget == self.memarea:
                pid = self.memrender.getclick(self.startx, self.starty)
            print self.dgather.data[pid].command, self.dgather.data[pid].data
            self.pl.selectpid(pid)
            self.selected_pid = pid
            self.cpurender.selected_pid = pid
            self.memrender.selected_pid = pid
        return True
        
    def runGTK(self):
        #self.timeout_add(20, self.mainloop)
        #gobject.timeout_add(500, self.tmrender.paintTreemaps(self.tmrender.cr, self.tmrender.width, self.tmrender.height))
        gtk.main()
        
    def mainloop(self):
        while True:
            # Process all pending events.
            while gtk.events_pending():
                gtk.main_iteration(False)
            # Generate an expose event (could just draw here as well).
            self.queue_draw()
        
    def initDataThread(self):
        self.dgather = datagather(self.data, self.dlock,self.pl)
        #self.dgather.init(self.data, self.dlock)
        self.dgather.start()    # Hmmm.. this seems dangerous as we need to access data from multiple threads
        #self.dgather.fauxrun()
        print "Started"
        
        #self.tmrender = tmrender(self.dgather, self.dlock, self.cpuarea)
        #self.tmrender.start()
        
        #Temporary to see if it works
        #global handle_id
        #if handle_id is not None:
        #    self.cpuarea.disconnect(handle_id)
        #handle_id = self.cpuarea.connect("expose-event", self.qd)
        #self.cpuarea.queue_draw()
        self.sdraw = splittreemap.splittreemap([])
    
    def qd(self, thing1, thing2):
        print 'qd'
        #cr = self.cpuarea.window.cairo_create()
        #cr.rectangle(0,0,10,10)
        #cr.fill()
        #self.cpuarea.queue_draw()
        
    def paintTreemaps(self, null1=0, null2=0):
        cr = self.cpuarea.window.cairo_create()
        width, height = self.cpuarea.window.get_size()
        
                    
        #while(1):
        print "drawing"
        #    time.sleep(0.5)
        self.dlock.acquire()
        # put the data all into nice format
        #items = self.dgather.nicecpu(0, self.dgather.officialtime)
        items, pids = self.dgather.cpuanim()
        #items = (0.5, 0.25, 0.125, 0.125)
        # call the painter on each category
        rects = self.sdraw.layout(0, 0, width, height, items, pids)
        for r in rects:
            #print r.x, r.y, r.w, r.h
            x = r.x; y = r.y; w = r.w; h = r.h;
            #r = pid % 255
            #g = (pid + 90) % 255
            #b = (pid + 180) % 255
            rd = numpy.random.random()
            g = numpy.random.random()
            b = numpy.random.random()
            a = 1
            cr.set_source_rgba(rd, g, b, a)
            cr.rectangle(r.x, r.y, r.w, r.h)
            cr.fill()
        self.dlock.release()
        #self.cpuarea.queue_draw()
        #self.queue_draw()
        
        pass
        
if __name__ == '__main__':
    tm = treemon()
    tm.start()
    
    pass