import os
import random
import cv2
import numpy as np

from utils import *

class Model:
    def __init__(self, imFolder, gtFolder):
        self.i = 0 # image counter
        self.imFolder = imFolder
        self.gtFolder = gtFolder
        self.delete = False # is the delete toggle activated?

        self.anomalyTypeDict = {'Both': 255, 'Mov': 155, 'Ap': 100}
        self.anomalySelectedType = 'Both'

        # sorted list of all TIFF file in imFolder
        self.imFiles = sorted([f for f in os.listdir(self.imFolder) if '.tif' in f])

        self.loadAll()

    # count the number of pixels, from a certain ROI, that are > 0
    def contourArea(self, gt, firstRow, firstCol, lastRow, lastCol):
        # gt is a np.uint8
        roi = gt[firstRow:lastRow,firstCol:lastCol]
        return np.sum(roi > 0)


    # computes the avg flow for foreground pixels in a ROI
    def avgFlow(self, flow, gt, firstRow, firstCol, lastRow, lastCol):
        nPixels = self.contourArea(bwIm, firstRow, firstCol, lastRow, lastCol)

        roiFlowCols = flow[firstRow:lastRow,firstCol:lastCol,0]
        roiFlowRows = flow[firstRow:lastRow,firstCol:lastCol,1]
        roi = gt[firstRow:lastRow,firstCol:lastCol]

        return np.mean(roiFlowRows[roi == 255]), np.mean(roiFlowCols[roi == 255])

    def loadAll(self):
        self.im = cv2.imread(self.imFolder + self.imFiles[self.i])
        self.gt = self.loadGT()
        self.contours = []
        self.fill()

    def loadGT(self):
        # case 1: GT already exists
        self.gtFile = self.gtFolder + self.imFiles[self.i].replace('.tif', '.bmp')
        if os.path.isfile(self.gtFile):
            return cv2.imread(self.gtFile, cv2.IMREAD_GRAYSCALE)

        # case 2: GT can not be estimated for the first image
        if self.i == 0:
            return np.zeros((self.im.shape[0], self.im.shape[1]), dtype=np.uint8)

        # TODO:
        # case 3: GT can not be estimated, because the previous image has no GT
        # gtPrevFile = self.gtFolder + self.imFiles[self.i-1].replace('.tif', '.bmp')
        # if not os.path.isfile(gtPrevFile):
        #     return np.zeros((self.im.shape[0], self.im.shape[1]), dtype=np.uint8)

        # case 4: GT can be estimated
        prevIm = cv2.imread(self.imFolder + self.imFiles[self.i-1], cv2.IMREAD_GRAYSCALE)
        currentIm = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prevIm, currentIm, \
                                                    None, 0.5, 3, 15, 3, 5, 1.2, 0)
        #gtPrev = cv2.imread(gtPrevFile, cv2.IMREAD_GRAYSCALE)
        gtPrev = self.gt.copy()
        gt = np.zeros((self.im.shape[0], self.im.shape[1]), dtype=np.uint8)
        for c in self.contours:
            r = cv2.boundingRect(c)
            i1, j1, i2, j2 = rect2coordinates(r)
            fx, fy = self.avgFlow(flow, self.gt, i1, j1, i2, j2)
            fi = np.round(fx)
            fj = np.round(fy)

            gt[i1+fi:i2+fi,j1+fj:j2+fj] = gtPrev[i1:i2,j1:j2]

        return gt

    def imfill(self, im):
        print 'IM FILL'
        imAux = gt = np.zeros((im.shape[0], im.shape[1]), dtype=np.uint8)
        imAux[im > 0] = 255

        aux = cv2.copyMakeBorder(imAux,5,5,5,5,0)

        nRows, nCols = aux.shape[:2]
        m = np.zeros((nRows+2, nCols+2), np.uint8)
        cv2.floodFill(aux, m, (0,0), 255);

        aux = cv2.bitwise_not(aux)[5:-5, 5:-5]
        ret = aux | imAux
        ret[im > 0] = im[im > 0]

        return ret

    # controler interface
    def annotate(self, row1, col1, row2, col2):
        if self.delete:
            self.gt[row1:row2+1, col1:col2+1] = 0
        else:
            self.gt[row1:row2+1, col1:col2+1] = self.anomalyTypeDict[self.anomalySelectedType]

    def fill(self):
        self.gt = self.imfill(self.gt)

        # findContours modifies the input image
        _, self.contours, _ = cv2.findContours(self.gt.copy(), \
                                                cv2.RETR_LIST, \
                                                cv2.CHAIN_APPROX_SIMPLE)
        print len(self.contours)
        for c in self.contours:
            r = cv2.boundingRect(c)
            i1, j1, i2, j2 = rect2coordinates(r)
            print 'area = %d' % (self.contourArea(self.gt, i1, j1, i2, j2))

    def nextIm(self):
        print self.gt[self.gt > 0]
        cv2.imwrite(self.gtFile, self.gt)
        print self.gtFile
        if self.i < (len(self.imFiles) - 1):
            self.i += 1
            self.loadAll()

    def prevIm(self):
        print self.gt[self.gt > 0]
        cv2.imwrite(self.gtFile, self.gt)
        if self.i > 0:
            self.i -= 1
            self.loadAll()

    def switchDel(self):
        self.delete = not self.delete

    def selectByPiont(self, row, col):
        for c in self.contours:
            if cv2.pointPolygonTest(c, (col,row), False) >= 0:
                r = cv2.boundingRect(c)
                i1, j1, i2, j2 = rect2coordinates(r)
                return i1, j1, i2, j2

        return -1, -1, -1, -1

    def setAnomalyType(self, firstRow, firstCol, lastRow, lastCol):
        roi = self.gt[firstRow:lastRow,firstCol:lastCol]
        print roi
        roi[roi > 0] = self.anomalyTypeDict[self.anomalySelectedType]
        print 'aKIIIIIII'
        print roi
        print self.anomalyTypeDict[self.anomalySelectedType]
        self.gt[firstRow:lastRow,firstCol:lastCol] = roi[:,:]
        print self.gt[firstRow:lastRow,firstCol:lastCol]
