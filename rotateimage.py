import cv2
from os.path import expanduser

home = expanduser('~')

def rotate(imagepath,number):
    img = cv2.imread(imagepath)
    # get image height, width
    (h, w) = img.shape[:2]
    # calculate the center of the image
    center = (w / 2, h / 2)
    angle180 = 180
    scale = 1.0
    M = cv2.getRotationMatrix2D(center, angle180, scale)
    rotated180 = cv2.warpAffine(img, M, (w, h))
    cv2.imwrite(home+'/'+'xxxx'+str(number)+'rotate.jpeg',rotated180)
    path = home+'/'+'xxxx'+str(number)+'rotate.jpeg'
    return path
