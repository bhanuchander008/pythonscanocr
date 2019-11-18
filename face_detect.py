import random
import cv2
import sys
import os
from os.path import expanduser
from datetime import date, datetime
date = str(date.today())
home = expanduser('~')
directory_concatenation = home + '/'+date+'/'

CASCADE = "Face_cascade.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)
rand_int = random.randint(0, 10000)


def detect_faces(image_path, number):
    image = cv2.imread(image_path)
    file_path = image_path.strip(directory_concatenation)
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_path = os.path.join(home, 'xxxx'+str(number)+'face.jpeg')

    faces = FACE_CASCADE.detectMultiScale(
        image_grey, scaleFactor=1.16, minNeighbors=5, minSize=(30, 50), flags=0)
    for x, y, w, h in faces:
        sub_img = image[y-20:y+h+35, x-10:x+w+25]

        cv2.imwrite(face_path, sub_img)

        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)

        break

    return face_path
