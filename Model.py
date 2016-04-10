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

    def contourArea(self, bwIm, rect):
        # bwIm is a np.uint8 image that contains the filled contour and should only contain pixels that are equal to 0 or 255
        # rect is a opecv rectangle where the contour is
        return np.sum(bwIm[rect[1]:(rect[1]+rect[3]),rect[0]:(rect[0]+rect[2])])/255

    def avgFlow(self, flow, bwIm, rect):
        nPixels = self.contourArea(bwIm, rect)

        roiFlowCols = flow[rect[1]:(rect[1]+rect[3]),rect[0]:(rect[0]+rect[2]),0]
        roiFlowRows = flow[rect[1]:(rect[1]+rect[3]),rect[0]:(rect[0]+rect[2]),1]
        mask = bwIm[rect[1]:(rect[1]+rect[3]),rect[0]:(rect[0]+rect[2])]

        return np.mean(roiFlowRows[mask == 255]), np.mean(roiFlowCols[mask == 255])

    def loadAll(self):
        self.im = cv2.imread(self.imFolder + self.imFiles[self.i])
        self.gt = self.loadGT()
        self.contours = []
        self.fill()

    def loadGT(self):
        # case 1: GT already exists
        # gtFile = self.gtFolder + self.imFiles[self.i].replace('.tif', '.bmp')
        # if os.path.isfile(gtFile):
        #     return cv2.imread(gtFile, cv2.IMREAD_GRAYSCALE)

        # case 2: GT can not be estimated for the first image
        if self.i == 0:
            return np.zeros((self.im.shape[0], self.im.shape[1]), dtype=np.uint8)

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
            fx, fy = self.avgFlow(flow, self.gt, r)
            fi = np.round(fx)
            fj = np.round(fy)
            print 'fx=%lf, fy=%lf -> rows=%d, cols=%d' % (fx,fy,np.round(fx),np.round(fy))

            i1 = r[1]
            i2 = r[1] + r[3]
            j1 = r[0]
            j2 = r[0] + r[2]

            gt[i1+fi:i2+fi,j1+fj:j2+fj] = gtPrev[i1:i2,j1:j2]

        return gt

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

        # findContours modifies the input image
        _, self.contours, _ = cv2.findContours(self.gt.copy(), \
                                                cv2.RETR_LIST, \
                                                cv2.CHAIN_APPROX_SIMPLE)
        print len(self.contours)
        for c in self.contours:
            r = cv2.boundingRect(c)
            print 'area = %d' % (self.contourArea(self.gt, r))

    def nextIm(self):
        if self.i < (len(self.imFiles) - 1):
            self.i += 1
            self.loadAll()

    def prevIm(self):
        if self.i > 0:
            self.i -= 1
            self.loadAll()
