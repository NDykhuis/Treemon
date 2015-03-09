'''
Created on Nov 30, 2010

@author: nathand
'''
import pygtk
import gtk
import process2
import copy

class proclist(object):
    '''
    classdocs
    '''


    def __init__(self, window):
        '''
        Constructor
        '''
        
        vbox = gtk.VBox(False, 8)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        vbox.pack_start(sw, True, True, 0)

        #store = self.create_model()
        self.lstore = gtk.ListStore(int, str, float, float)
        self.lstore.set_sort_column_id(2, gtk.SORT_DESCENDING)
        store = self.lstore
        
        treeView = gtk.TreeView(store)
        treeView.connect("row-activated", self.on_activated)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        self.treeView = treeView
        #treeView.set_property('fixed-height-mode', True)

        self.create_columns(treeView)
        self.statusbar = gtk.Statusbar()
        
        vbox.pack_start(self.statusbar, False, False, 0)

        self.mywidge = vbox
        #return vbox
        #self.add(vbox)
        #self.show_all()

    def getWidget(self):
        return self.mywidge

    def create_model(self):
        store = gtk.ListStore(str, str, str, str)

        #for p in processes:
        #    store.append([p[0], p[1], p[2]])
        #for act in actresses:
        #    store.append([act[0], act[1], act[2]])

        return store
    
    def findrow(self, rows, val):
        if not rows: return None
        i = 0
        for row in rows:
            if row[0] == val:
                return i
            i += 1
        return None
        
    def update_data(self, processes):
        tv = self.treeView
        ls = self.lstore
        #bs = self.bstore
        #ts = tv.get_model() 
        lastpid = None
        
        #self.treeView.set_model(bs)
        scol, stype = ls.get_sort_column_id()
        #fpath, fcol = tv.get_cursor()
        #print fpath, fcol
        treeselection = tv.get_selection()
        (model, iter) = treeselection.get_selected()
        #lastpid = model[iter][0]
        if model is not None and iter is not None:
            lastpid = model[iter][0]
        #print iter
        self.treeView.freeze_child_notify()
        self.treeView.set_model()
        ls.clear()
        ls.set_default_sort_func(lambda *args: -1)
        ls.set_sort_column_id(-1, gtk.SORT_ASCENDING)
        #newstore = gtk.ListStore(str, str, str, str)
        
        append = ls.append
        for p in processes:
            append(processes[p].getrow())
        
        #for pid, proc in processes.iteritems():
        #    #ls.append((pid, proc.command, proc.data["cpu"], proc.data["mem"]))
        #    ls.append(proc.getrow())

        if scol is not None:
            ls.set_sort_column_id(scol, stype)
        tv.set_model(ls)
        tv.thaw_child_notify()
        
        #lastpid = 401
        if lastpid is not None:
            i = self.findrow(ls, lastpid)
            if i is not None:
                #print "ICOMMA:", (i,)
                treeselection.select_path(i)
                #tv.set_cursor(3)
        #if iter is not None:
        #    treeselection.select_iter(iter)
        #if fpath is not None:
        #    tv.set_cursor(fpath, fcol)
        
    def selectpid(self, pid):
        tv = self.treeView
        ls = self.lstore
        i = self.findrow(ls, pid)
        treeselection = tv.get_selection()
        if i is not None:
            treeselection.select_path(i)
            #tv.set_cursor((i,))
        
        
    def create_columns(self, treeView):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("PID", rendererText, text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_expand(False)
        column.set_sort_column_id(0)    
        treeView.append_column(column)
        
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_expand(False)
        column.set_sort_column_id(1)    
        treeView.append_column(column)
        
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("CPU", rendererText, text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_expand(False)
        column.set_sort_column_id(2)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Mem", rendererText, text=3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_expand(False)
        column.set_sort_column_id(3)
        treeView.append_column(column)


    def on_activated(self, widget, row, col):
        print "AVTICATTED!"
        #model = widget.get_model()
        #text = model[row][0] + ", " + model[row][1] + ", " + model[row][2]
        #self.statusbar.push(0, text)

