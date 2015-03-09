'''
Created on Nov 17, 2010

@author: nathand
'''
import time

class Rectangle:
    def __init__(self, x,y,w,h, id=0):
        self.id = id; self.x = x; self.y = y; self.w = w; self.h = h;

class splittreemap(object):
    '''    classdocs    '''


    def __init__(self,items):
        '''        Constructor        '''
        # Items is a list of items to go in the treemap
        self.items = items
        self.sumitems = []
        lastitem = 0
        for i in range(len(self.items)):
            lastitem = lastitem + self.items[i]
            self.sumitems.append(lastitem)
        self.lastplace = {}
        
    def layout(self, x, y, w, h, items, ids):
        r = Rectangle(x,y,w,h)
        rlist = []
        items = [i for i in items if i != 0]
        return self.splitLayout(items, ids, r, rlist)
        
    # NEED TO HANDLE CASES WITH LOTS OF ZEROS
    def splitLayout(self, items, ids, r, rlist):
        if (len(items) == 0 or len(items) == 1 or sum(items) == 0):
            if len(ids) > 0:
                r.id = ids[0]
            rlist.append(r)
            return
        #if (len(items) == 1) {    # Should just use the whole rectangle
            #items.bounds = r;
            #splitLayout(items.children, r); // Layout the children within
        #}
        l1=[]; l2=[]; #Rectangle r1, r2;
        halfSize = sum(items) / 2.0;
        w1 = 0; tmp = 0; f = 0;
        # Pick out half the weight into l1, half into l2
        for i in range(len(items)):
            front = items[f];
            tmp = w1 + front;
            
            # Try to add some hysteresis - keep items from jumping back and forth
            if not ids[f] in self.lastplace:
                self.lastplace[ids[f]] = False
            if self.lastplace[ids[f]] == False:
                epsilon = 0.01*halfSize
            else:
                epsilon = -0.01*halfSize
            
            #epsilon = 0
            # Test if it got worse by picking another item
            if (abs(halfSize - tmp) + epsilon > abs(halfSize - w1)):
                if sum(l1) != 0:    # Must have at least 1 item in l1
                    break;
            # It was good to pick another
            #l1.enqueue(items[f]);
            l1.append(items[f])
            self.lastplace[ids[f]] = False
            f += 1
            w1 = tmp;
        # The rest of the items go into l2
        l2 = items[f:];
        id1 = ids[:f]   # This may not work
        id2 = ids[f:]
        for i in range(f, len(items)):
            self.lastplace[ids[f]] = True
        if r.w > r.h:
            r1 = Rectangle(r.x, r.y, r.w * sum(l1)/(sum(l1) + sum(l2)), r.h);
            r2 = Rectangle(r.x + r1.w, r.y, r.w - r1.w, r.h);
        else:
            r1 = Rectangle(r.x, r.y, r.w, r.h * sum(l1)/(sum(l1) + sum(l2)));
            r2 = Rectangle(r.x, r.y + r1.h, r.w, r.h - r1.h);
        # rlist.append(r1); rlist.append(r2)
        self.splitLayout(l1, id1, r1, rlist);
        self.splitLayout(l2, id2, r2, rlist);
        
        # DRAW THE RECTANGLES!
        return rlist;
        