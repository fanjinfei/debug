#!/usr/bin/env python
import random, math, gc
import sys
from PyQt4 import QtGui
from PyQt4.QtCore import QTimer
 
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import scipy.spatial as spatial
import numpy as np
from collections import defaultdict


def _get_data():
    data= []
    for i in range (0, 100):
        p = ( round( random.uniform(1, 10), 4), round(random.uniform(2,20), 4) )
        data.append(p)
    return data
class MData():
    def __init__(self, data):
        self.data = data
        (self.xin, self.yin), (self.xax, self.yax) = data[0], data[1]
        for (x,y) in data:
            if x < self.xin: self.xin = x
            if y < self.yin: self.yin = y
            if x > self.xax: self.xax = x
            if y > self.yax: self.yax = y
    def dist(self, i, j):
        (x1,y1) =  self.data[i]
        (x2,y2) = self.data[j]
        x1 = x1-x2
        y1 = y1 - y2
        return math.sqrt( x1*x1 + y1*y1)
    def getNN(self): # get the most NN
        ci, cj,cl = None, None, None
        data = self.data
        for i in range(0,len(data)-1):
            for j in range(i+1, len(data)):
                l = self.dist(i,j)
                if cl == None or cl > l:
                    ci,cj,cl = i,j,l
        if data[ci][0] > data[cj][0]: #ci in the left of cj
            ci,cj= cj, ci
        self.ci, self.cj, self.cl = ci, cj, cl
    def getRecordSets(self): # [ ( 2,3), (8, 7, 10) ], [2,3] will be kept
        self.getNN()
        ci, cj, cl = self.ci, self.cj, self.cl
        #cut grid, uniform in directions
        (x1,y1), (x2,y2) = self.data[ci], self.data[cj]
        xin,yin,xax,yax = self.xin, self.yin, self.xax, self.yax
        d1 = max( abs( x1-x2), abs(y1-y2))
        d1 *= 1.0001 #0.0001 delta
        dp = 1 if y2 >= y1 else -1 #left-bottom or left-top ?, make sure at least one is reduced

        #relocate p to left-botton of grid
        data = {} #defaultdict( type ({})) defaultdict(lambda: defaultdict(int))
        merged = defaultdict(lambda: defaultdict(list))
        for (x,y) in self.data:
            nx, ny = (x-x1)/d1, (y-y1)/d1
            px,py = math.floor(nx), ( math.floor(ny) if dp==1 else math.ceil(ny))
            if not data.get(px):
                data[px] = {}
            data[px][py] = (px*d1 + x1, py*d1 + y1)

            merged[px][py].append( (x,y) )

        ndata = []
        for x, ly in data.iteritems():
            for y, p in ly.iteritems():
                ndata.append( p)
        mdata = []
        for x, ly in merged.iteritems():
            for y, ps in ly.iteritems():
                if len(ps) > 1:
                    mdata.append(ps)
        return ndata, mdata
def _test2():
    md = MData( _get_data())
    md.getRecordSets()
    #sys.exit(0)
def fmt(x, y):
    return 'x: {x:0.2f}\ny: {y:0.2f}'.format(x=x, y=y)

class FollowDotCursor(object):
    """Display the x,y location of the nearest data point.
    http://stackoverflow.com/a/4674445/190597 (Joe Kington)
    http://stackoverflow.com/a/13306887/190597 (unutbu)
    http://stackoverflow.com/a/15454427/190597 (unutbu)
    """
    def __init__(self, ax, x, y, tolerance=5, formatter=fmt, offsets=(-20, 20), canvas = None, plt=None):
        try:
            x = np.asarray(x, dtype='float')
        except (TypeError, ValueError):
            x = np.asarray(mdates.date2num(x), dtype='float')
        y = np.asarray(y, dtype='float')
        mask = ~(np.isnan(x) | np.isnan(y))
        x = x[mask]
        y = y[mask]
        self._points = np.column_stack((x, y))
        self.offsets = offsets
        y = y[np.abs(y-y.mean()) <= 3*y.std()]
        self.scale = x.ptp()
        self.scale = y.ptp() / self.scale if self.scale else 1
        self.tree = spatial.cKDTree(self.scaled(self._points))
        self.formatter = formatter
        self.tolerance = tolerance
        self.ax = ax
        self.fig = ax.figure
        self.ax.xaxis.set_label_position('bottom') #top
        self.dot = ax.scatter(
            [x.min()], [y.min()], s=130, color='green', alpha=0.7)
        self.annotation = self.setup_annotation()
        if plt:
            plt.connect('motion_notify_event', self)
        if canvas:
            self.cid = canvas.mpl_connect('motion_notify_event', self)

    def __del__(self):
        pass #print ("cursor deleted")
    def scaled(self, points):
        points = np.asarray(points)
        return points * (self.scale, 1)

    def __call__(self, event):
        ax = self.ax

        #line = ax.get_lines()[0]
        contained, infos = self.dot.contains(event) # line.contains(event)
        if not contained:                                # eventually exited
            self.annotation.set_visible(False)
        else:
            if not self.annotation.get_visible():             # is entered
                self.annotation.set_visible(True)         # event.inaxes is always the current axis. If you use twinx, ax could be
            '''xdata, ydata = line.get_data()
            ind = infos['ind'][0]
            annotation = self.annotations[xdata[ind], ydata[ind]]
            if not annotation.get_visible():             # is entered
                annotation.set_visible(True)         # event.inaxes is always the current axis. If you use twinx, ax could be
            '''
        # a different axis.
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
        elif event.inaxes is None:
            return
        else:
            inv = ax.transData.inverted()
            x, y = inv.transform([(event.x, event.y)]).ravel()
        annotation = self.annotation
        x, y = self.snap(x, y)
        annotation.xy = x, y
        annotation.set_text(self.formatter(x, y))
        self.dot.set_offsets((x, y))
        bbox = ax.viewLim
        event.canvas.draw()

    def setup_annotation(self):
        """Draw and hide the annotation box."""
        annotation = self.ax.annotate(
            '', xy=(0, 0), ha = 'right',
            xytext = self.offsets, textcoords = 'offset points', va = 'bottom',
            bbox = dict(
                boxstyle='round,pad=0.5', fc='yellow', alpha=0.75),
            arrowprops = dict(
                arrowstyle='->', connectionstyle='arc3,rad=0'))
        return annotation

    def snap(self, x, y):
        """Return the value in self.tree closest to x, y."""
        dist, idx = self.tree.query(self.scaled((x, y)), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            # IndexError: index out of bounds
            return self._points[0]

class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
 
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.cursor = None
        self.canvas = FigureCanvas(self.figure)
 
         
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()
 
        # Just some button 
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

 
        self.button1 = QtGui.QPushButton('Zoom')
        self.button1.clicked.connect(self.zoom)
         
        self.button2 = QtGui.QPushButton('Pan')
        self.button2.clicked.connect(self.pan)
         
        self.button3 = QtGui.QPushButton('Home')
        self.button3.clicked.connect(self.home)
 
        self.button4 = QtGui.QPushButton('Scale')
        self.button4.clicked.connect(self.scale)

        self.button5 = QtGui.QPushButton('Exit')
        self.button5.clicked.connect(self.equit)
 
        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.button4)
        layout.addWidget(self.button5)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        self.setLayout(layout)
        
        self.data = _get_data()
        self.mdata = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        #self.timer.start(1000)
    def tick(self):
        pass
        #print 'tick'

    def home(self):
        self.toolbar.home()
    def zoom(self):
        self.toolbar.zoom()
    def pan(self):
        self.toolbar.pan()
    def equit(self):
        sys.exit(0)

    def scale(self):
        '''data = []
        for (x,y) in self.data:
            data.append( (x,y) )'''
        md = MData(self.data)
        self.data, self.mdata= md.getRecordSets()
        self.plot()
         
    def plot(self):
        ''' plot some random stuff 
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        ax.plot(data, '*-')
        self.canvas.draw()'''
        #self.ax.hold(False)
        #y = [ v[0] for v in self.data]
        #z = [ v[1] for v in self.data] #horizon
        x,y = zip (*self.data)
        if self.ax:
            self.figure.delaxes( self.ax)
            del self.ax
            if self.cursor:
                self.canvas.mpl_disconnect(self.cursor.cid)
                del self.cursor
            self.ax = self.figure.add_subplot(111)
        #self.ax.clear()
        gc.collect()
        self.ax.scatter(x,y, s=4, color='blue', picker=True)

        '''a,b = [1,2,3], [4,5,6]
        c = zip(a,b)
        d, e = zip( *c)
        self.ax.scatter(d,e, s=3, color='red', picker=True)'''
        m,n = (), ()
        for ps in self.mdata:
            d,e = zip (*ps)
            m, n = m+d, n+e
            self.ax.scatter(d,e, s=2, color='red')

        self.cursor = FollowDotCursor(self.ax, x, y, tolerance=20, canvas=self.canvas)
        self.canvas.draw()
 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
 
    main = Window()
    main.setWindowTitle('Simple QTpy and MatplotLib example with Zoom/Pan')
    main.show()
 
    sys.exit(app.exec_())

def mytest():
    data = _get_data()

    '''
    y=[2.56422, 3.77284,3.52623,3.51468,3.02199]
    z=[0.15, 0.3, 0.45, 0.6, 0.75]
    n=[58,651,393,203,123]
    ax.scatter(z, y)
    for i, txt in enumerate(n):
        ax.annotate(txt, (z[i],y[i]))
    '''
    y = [ v[0] for v in data]
    z = [ v[1] for v in data] #horizon
    def onpick3(event):
        ind = event.ind
        txt = "{0:.5g},{1:.5g}".format(z[ind], y[ind])
        txt = "{0:.5g},{1:.2f}".format(z[ind], y[ind])
        print 'onpick3 scatter:', ind, txt #npy.take(y, ind)


    '''
    def on_plot_hover(event):
        for curve in plot.get_lines():
            if curve.contains(event)[0]:
                print "over %s" % curve.get_gid()
    fig.canvas.mpl_connect('motion_notify_event', on_plot_hover) 
    '''

    fig, ax = plt.subplots()
    ax.scatter(z,y, picker=True)

    fig.canvas.mpl_connect('pick_event', onpick3)
    cursor = FollowDotCursor(ax, z, y, tolerance=20)

    '''
    # too condensed to be read
    for i, txt in enumerate(data):
        a = ( int(txt[0]), int(txt[1]))
        ax.annotate( a, (z[i],y[i]))
    '''    

    plt.xlabel("x direction")
    plt.ylabel("y direction")
    plt.title("sample matplot -- tutor 1")
    plt.grid(True)
    plt.show()

