import os

import cv2
import numpy as np

class Model:
    def __init__(self, imFolder, gtFolder):
        self.i = 0
        self.imFolder = imFolder
        self.gtFolder = gtFolder

        self.imFiles = sorted([f for f in os.listdir(self.imFolder) if '.tif' in f])

        self.loadAll()

    def loadAll(self):
        self.im = cv2.imread(self.imFolder + self.imFiles[self.i])
        self.gt = self.loadGT(self.imFiles[self.i])

    def loadGT(self, imFile):
        gtFile = imFile.replace('.tif', '.bmp')

        if os.path.isfile(self.gtFolder + gtFile):
            return cv2.imread(self.gtFolder + gtFile, cv2.IMREAD_GRAYSCALE)

        return np.zeros((self.im.shape[0], self.im.shape[1]), dtype=np.uint8)

    def imfill(self, im):
        aux = cv2.copyMakeBorder(im,5,5,5,5,0)

        h, w = aux.shape[:2]
        m = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill(aux, m, (0,0), 255);

        aux = cv2.bitwise_not(aux)[5:-5, 5:-5]
        ret = aux | im

        return ret

    # controler interface
    def annotate(self, row1, col1, row2, col2):
        self.gt[row1:row2+1, col1:col2+1] = 255

    def fill(self):
        self.gt = self.imfill(self.gt)

    def nextIm(self):
        if self.i < (len(self.imFiles) - 1):
            self.i += 1
            self.loadAll()

    def prevIm(self):
        if self.i > 0:
            self.i -= 1
            self.loadAll()
