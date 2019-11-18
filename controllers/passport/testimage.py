from datetime import datetime
from flask import request
from config import basedir
from flask_restful import reqparse,Resource
from vision import detect_text
import os
import logging, logging.config, yaml
import base64
from face_detect import detect_faces
from os.path import expanduser
from datetime import date, datetime
from tempfile import TemporaryFile
t = TemporaryFile()

home = expanduser('~')
#print("home////////////",home)
date = str(date.today())




"""
CONFIG_PATH = os.path.join(basedir,'loggeryaml/passportlogger.yaml')
logging.config.dictConfig(yaml.load(open(CONFIG_PATH)))
logger = logging.getLogger('imagepassports')"""



class ImageDetail(Resource):

    def __init__(self):
          pass


    def post(self):
         #file = request.form

         #base=file['Passport_Image']
         image = request.files['Passport_Image']

         image_string = base64.b64encode(image.read()).decode()


         base= image_string.encode()
        
         details= detect_text(image_string)
         print("......................:",details)
         strps_base =image_string.strip('')[1]

        # print("=============",image_string)

        # directory =  home +'/'+ date
         #print("-------------------------",directory)
         #if not os.path.exists(directory):
            #print ("path doesn't exist. trying to make")
            #os.mkdir(directory)
        # name = details['Passport_Document_No'] + '_' +details['FamilyName']
         #filename = directory+'/'+name+'.jpeg'  # I assume you have a way of picking unique filenames
        # t = TemporaryFile(filename)
         base= image_string.encode()
         print = ("tnkdfkn:",base)
         filename = home +'/'+'document.jpeg'  # I assume you have a way of picking unique filenames
         with open(filename, 'wb') as f:
             f.write(base)

        # fullimage_size = ('{:,.0f}'.format(os.path.getsize(filename)/float(1<<10))+" KB")
         face=detect_faces(filename)
         #os.remove(filename)#print("data return",face)
         with open(face, 'rb') as image:
             image_string_face = base64.b64encode(image.read()).decode()
         #print("image_string:",image_string)
         logger.info("Data added successfully to passport")
         details['face']=image_string_face

         #logger.info("Data added successfully to passport")
         return details
