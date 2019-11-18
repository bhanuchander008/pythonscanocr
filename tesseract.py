from PIL import Image,ImageEnhance,ImageFilter
import pytesseract
import cv2
import os
import imutils
import numpy as np
from extract_text import detect_api

def imagetext(image):
    images=image
    def imgenhance(imgpath):
        img = Image.open(imgpath).convert("L")
        img = img.filter(ImageFilter.SHARPEN())
        enhancer = ImageEnhance.Brightness(img)
        out = enhancer.enhance(1.8)
        nx, ny = out.size
        print("imagesize:",nx,ny)
        out = out.resize((int(nx*1.5), int(ny*1.5)), Image.ANTIALIAS)
        print("size:",out.size)
        out.save("/home/caratred/copy/passport/Cleaned1.jpeg",quality=94)
        text = pytesseract.image_to_string(Image.open('/home/caratred/copy/passport/Cleaned1.jpeg'))
        os.remove('/home/caratred/copy/passport/Cleaned1.jpeg')
        extract=text.split('\n')
        print(extract)
        return extract
    offence=[imgenhance(x) for x in images]
    offence=[y for x in offence for y in x]
    offence = [x for x in offence if x!='']
    print("offence:",offence)
    extracted_text = detect_api(offence)
   
    return extracted_text
