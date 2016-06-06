import ttk
import cv2

from PIL import Image, ImageTk

class View:
    def __init__(self, master):
        self.zoom = 1.0

        self.sRow1 = self.sRow2 = self.sCol1 = self.sCol2 = -1

        # TODO: possible bug
        self.im = None
        self.gt = None

        self.bgFrame = ttk.Frame(master)
        self.bgFrame.pack(side='right')

        # top frame
        self.topFrame = ttk.Frame(self.bgFrame)
        self.topFrame.pack(side='top')

        self.labelIm = ttk.Label(self.topFrame)
        self.labelIm.pack(side='left')

        self.labelGT = ttk.Label(self.topFrame)
        self.labelGT.pack(side='right')

        # bottom frame
        self.bottomKeysFrame = ttk.Frame(self.bgFrame)
        self.bottomKeysFrame.pack(side='top')

        self.btPrev = ttk.Button(self.bottomKeysFrame, text='Prev')
        self.btPrev.pack(side='left')

        self.btNext = ttk.Button(self.bottomKeysFrame, text='Next')
        self.btNext.pack(side='right')

        self.statusFrame = ttk.Frame(self.bgFrame)
        self.statusFrame.pack(side='bottom')

        self.labelAnomalyType = ttk.Label(self.statusFrame, text='Anomaly Type: None')
        self.labelAnomalyType.pack(side='bottom')

        # side panel
        # self.sidePanel = ttk.Frame(master)
        # self.sidePanel.pack(side='left')
        #
        # self.bt1 = ttk.Button(self.sidePanel, text='BT1')
        # self.bt1.pack(side='top')
        #
        # self.bt2 = ttk.Button(self.sidePanel, text='BT2')
        # self.bt2.pack(side='top')

    def zoomIn(self):
        self.zoom += 0.1
        self.updateImages()

    def zoomOut(self):
        if self.zoom > 0.1:
            self.zoom -= 0.1
            self.updateImages()

    def updateImages(self, im=None, gt=None):
        if im is not None:
            self.im = im

        if gt is not None:
            self.gt = gt
            self.gtView = cv2.cvtColor(self.gt, cv2.COLOR_GRAY2BGR)
            self.sRow1 = self.sRow2 = self.sCol1 = self.sCol2 = -1
        elif self.sRow1 != -1:
            print '(%d,%d) -> (%d,%d)' % (self.sRow1,self.sCol1,self.sCol2,self.sRow2)
            self.gtView = cv2.cvtColor(self.gt, cv2.COLOR_GRAY2BGR)
            cv2.rectangle(self.gtView, (self.sCol1,self.sRow1), (self.sCol2,self.sRow2), color=(0,0,255))
        elif self.sRow1 == -1:
            self.gtView = cv2.cvtColor(self.gt, cv2.COLOR_GRAY2BGR)

        imAux = cv2.resize(self.im, dsize=(0,0), fx=self.zoom, fy=self.zoom, \
                            interpolation=cv2.INTER_NEAREST)
        gtAux = cv2.resize(self.gtView, dsize=(0,0), fx=self.zoom, fy=self.zoom, \
                            interpolation=cv2.INTER_NEAREST)

        #imAux[:,:,1] |= gtAux[:,:,1]
        imAux[gtAux[:,:,1] > 0, 1] = 255

        self.setImage(self.labelIm, imAux)
        self.setImage(self.labelGT, gtAux)

    def drawSelection(self, row1, col1, row2, col2):
        self.sRow1 = row1
        self.sRow2 = row2
        self.sCol1 = col1
        self.sCol2 = col2
        self.updateImages()

    def cv2photo(self, im):
        photo = Image.fromarray(im)
        photo = ImageTk.PhotoImage(image=photo)

        return photo

    def setImage(self, label, im):
        photo = self.cv2photo(im)

        # the image needs to be set two times due to this issue (http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm)
        label.config(image=photo)
        label.image = photo

    def setAnomalyType(self, typeName):
        newText = 'Anomaly Type: ' + typeName
        self.labelAnomalyType.config(text=newText)
        self.labelAnomalyType.text = newText
