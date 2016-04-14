# converts a OpenCV rect [firstCol, width, firstRow, height]
#                     to [firstRow, firstCol, lastRow, lastCol]
def rect2coordinates(rect):
    return rect[1], rect[0], (rect[1]+rect[3]), (rect[0]+rect[2])
