import Tkinter
import ttk

import cv2

from View import *
from Model import *

from utils import *

class Controller:
    def __init__(self, imFolder, gtFolder):
        self.app = Tkinter.Tk()

        self.app.title("Video Annotation")

        self.model = Model(imFolder, gtFolder)

        self.brushSize = 3 #TODO

        self.view = View(self.app)
        self.setCommands()

    def setCommands(self):
        self.view.labelIm.bind('<B1-Motion>', self.mouseMovAnnotationImage)
        self.view.labelIm.bind('<ButtonRelease-1>', self.mouseReleaseAnnotationImage)

        self.view.btPrev.bind('<Button-1>', self.prevButtonClick)
        self.app.bind('<Left>', self.prevButtonClick)

        self.view.btNext.bind('<Button-1>', self.nextButtonClick)
        self.app.bind('<Right>', self.nextButtonClick)

        self.app.bind('+', self.plusKey)
        self.app.bind('-', self.minusKey)

        self.updateView()

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
        row = event.y / self.view.zoom
        col = event.x / self.view.zoom

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

    def plusKey(self, event):
        self.view.zoomIn()

    def minusKey(self, event):
        self.view.zoomOut()
