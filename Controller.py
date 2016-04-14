import Tkinter
import ttk

import cv2

from View import *
from Model import *

from utils import *

class Controller:
    def __init__(self, imFolder, gtFolder):
        self.app = Tkinter.Tk()

        # self.app.style = ttk.Style()
        # self.app.style.theme_use('default')

        self.app.title('Video Annotation')

        self.model = Model(imFolder, gtFolder)

        # init flags
        self.brushSize = 3 #TODO

        self.view = View(self.app)
        self.setCommands()

    def setCommands(self):
        self.view.labelIm.bind('<B1-Motion>', self.mouseMovAnnotationImage)
        self.view.labelIm.bind('<ButtonRelease-1>', self.mouseReleaseAnnotationImage)

        self.view.labelGT.bind('<ButtonPress-1>', self.mousePressGT)
        self.view.labelGT.bind('<B1-Motion>', self.mouseMovGT)
        self.view.labelGT.bind('<ButtonRelease-1>', self.mouseReleaseGT)

        self.view.btPrev.bind('<ButtonPress-1>', self.prevButtonClick)
        self.app.bind('<Left>', self.prevButtonClick)

        self.view.btNext.bind('<ButtonPress-1>', self.nextButtonClick)
        self.app.bind('<Right>', self.nextButtonClick)

        self.app.bind('+', self.plusKey)
        self.app.bind('-', self.minusKey)

        self.app.bind('d', self.delKey)

        self.app.bind('1', self.anomalyTypeKey)
        self.app.bind('2', self.anomalyTypeKey)
        self.app.bind('3', self.anomalyTypeKey)
        self.view.setAnomalyType(self.model.anomalySelectedType)

        self.updateView()

    def xy2rowcol(self, x, y):
        return y / self.view.zoom, x / self.view.zoom

    def run(self):
        self.app.mainloop()

    def updateView(self):
        self.view.updateImages(self.model.im.copy(), self.model.gt)

    def nextButtonClick(self, event):
        self.model.nextIm()
        self.updateView()

    def prevButtonClick(self, event):
        self.model.prevIm()
        self.updateView()

    def mouseMovAnnotationImage(self, event):
        row, col = self.xy2rowcol(event.x, event.y)

        nRows = self.model.gt.shape[0]
        nCols = self.model.gt.shape[1]

        if row >= 0 and row < nRows and col >= 0 and col < nCols:
            d = self.brushSize/2
            self.model.annotate(row-d,col-d,row+d,col+d)
            self.updateView()

        print '(%d, %d)' % (row, col)

    def mouseReleaseAnnotationImage(self, event):
        self.model.fill()
        self.updateView()

    def mousePressGT(self, event):
        self.row1gt, self.col1gt = self.xy2rowcol(event.x, event.y)
        print 'p1 = (%d, %d)' % (self.row1gt, self.col1gt)

    def mouseMovGT(self, event):
        row, col = self.xy2rowcol(event.x, event.y)
        print 'p = (%d, %d)' % (row, col)

    def mouseReleaseGT(self, event):
        row, col = self.xy2rowcol(event.x, event.y)
        print 'p1 = (%d, %d) -> p2 = (%d, %d)' % (row, col, self.row1gt, self.col1gt)

        if row == self.row1gt and col == self.col1gt:
            print 'click!!!'
            row1, col1, row2, col2 = self.model.selectByPiont(row, col)
            if row1 != -1:
                self.model.setAnomalyType(row1, col1, row2, col2)
            print 'select (%d, %d) -> (%d, %d)' % (row1, col1, row2, col2)
            self.view.drawSelection(row1, col1, row2, col2)

    def plusKey(self, event):
        self.view.zoomIn()

    def minusKey(self, event):
        self.view.zoomOut()

    def delKey(self, event):
        self.model.switchDel()

    def anomalyTypeKey(self, event):
        t = int(event.char)
        key = self.model.anomalyTypeDict.keys()[t-1]
        self.model.anomalySelectedType = key
        self.view.setAnomalyType(key)
