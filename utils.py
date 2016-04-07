import numpy as np
import cv2

from PIL import Image, ImageTk

def cv2photo(im):
    photo = Image.fromarray(im)
    photo = ImageTk.PhotoImage(image=photo)

    return photo

def setLabelImPhoto(label, photo):
    # the image needs to be set two times due to this issue (http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm)
    label.config(image=photo)
    label.image = photo

def setLabelImCV(label, im):
    photo = cv2photo(im)
    setLabelImPhoto(label, photo)

def imfill(im):
    aux = cv2.copyMakeBorder(im,5,5,5,5,0)

    h, w = aux.shape[:2]
    m = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(aux, m, (0,0), 255);

    aux = cv2.bitwise_not(aux)[5:-5, 5:-5]
    ret = aux | im

    return ret
