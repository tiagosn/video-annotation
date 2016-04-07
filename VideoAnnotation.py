import numpy as np
import cv2

import Tkinter
import ttk

from PIL import Image, ImageTk

from utils import *

class VideoAnotation:
    def __init__(self, folderIm, folderGT):
        self.folderIm = folderIm
        self.folderGT = folderGT

        self.app = Tkinter.Tk()

        self.bgFrame = ttk.Frame(self.app, width=800, height=600)
        self.bgFrame.pack()

        self.im = cv2.imread('/home/tiagosn/datasets/UCSD_Anomaly_Dataset.v1p2/UCSDped2/Test/Test007/001.tif')
        print self.im.dtype
        print self.im.shape
        imTk = Image.fromarray(self.im)
        imTk = ImageTk.PhotoImage(image=imTk)
        self.mask = np.zeros((self.im.shape[0], self.im.shape[1]), dtype=np.uint8)
        maskTk = Image.fromarray(self.mask)
        maskTk = ImageTk.PhotoImage(image=maskTk)

        self.topFrame = ttk.Frame(self.bgFrame)
        self.topFrame.pack()
        self.label = ttk.Label(self.topFrame, image=imTk)
        self.label.bind('<B1-Motion>', self.mouse_mov)
        self.label.bind('<ButtonRelease-1>', self.mouse_release)
        #label.bind('<Button-1>', mouse_mov)
        self.label.pack(side='left')
        self.label2 = ttk.Label(self.topFrame, image=maskTk)
        self.label2.pack(side='right')

        self.bottomKeysFrame = ttk.Frame(self.bgFrame)
        self.bottomKeysFrame.pack(side='bottom')
        self.btPrev = ttk.Button(self.bottomKeysFrame, text='Prev')
        self.btPrev.bind('<Button-1>', self.f_prev)
        self.btPrev.pack(side='left')
        self.btNext = ttk.Button(self.bottomKeysFrame, text='Next', command=self.f_next)
        self.btNext.pack(side='right')

        self.app.mainloop()

    def f_prev(self, event):
        print 'PREV!!!'

    def f_next(self):
        print 'NEXT!!!'

    def mouse_release(self, event):
        m = imfill(self.mask)
        self.mask[:,:] = m[:,:]
        setLabelImCV(self.label2, self.mask)

        self.im[:,:,1] |= self.mask
        setLabelImCV(self.label, self.im)

    def mouse_mov(self, event):
        row = event.y
        col = event.x
        if row >= 0 and row < self.mask.shape[0] and col >= 0 and col < self.mask.shape[1]:
            self.mask[row-3:row+3, col-3:col+3] = 255
            setLabelImCV(self.label2, self.mask)

            self.im[:,:,1] |= self.mask
            setLabelImCV(self.label, self.im)

        print '(%d, %d)' % (row, col)

v = VideoAnotation(folderIm, folderGT)
