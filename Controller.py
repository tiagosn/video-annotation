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

        self.view.btNext.bind('<Button-1>', self.nextButtonClick)

        self.view.updateImages(self.model.im.copy(), self.model.gt)

    def run(self):
        self.app.mainloop()

    def nextButtonClick(self, event):
        print 'next button click is not implemented yet!!!'

    def prevButtonClick(self, event):
        print 'prev button click is not implemented yet!!!'

    def mouseMovAnnotationImage(self, event):
        row = event.y
        col = event.x

        nRows = self.model.gt.shape[0]
        nCols = self.model.gt.shape[1]

        if row >= 0 and row < nRows and col >= 0 and col < nCols:
            d = self.brushSize/2
            self.model.annotate(row-d,col-d,row+d,col+d)
            self.view.updateImages(self.model.im.copy(), self.model.gt)

        print '(%d, %d)' % (row, col)

    def mouseReleaseAnnotationImage(self, event):
        self.model.fill()
        self.view.updateImages(self.model.im.copy(), self.model.gt)
