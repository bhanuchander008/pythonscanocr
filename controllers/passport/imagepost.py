from flask import request
from config import basedir
from flask_restful import reqparse, Resource
from vision import detect_text
import logging
import logging.config
import yaml
import base64
from face_detect import detect_faces
import os
from os.path import expanduser
from datetime import date, datetime
from exceptions import NoneType, textAnnotations
from rotateimage import rotate
import random
import traceback

home = expanduser('~')

date = str(date.today())


CONFIG_PATH = os.path.join(basedir, 'loggeryaml/passportlogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
logger = logging.getLogger('imagepassports')
startlog = logging.getLogger('imagepassports')
consolelog = logging.getLogger('passportdetails')


class PostImageDetail(Resource):

    def __init__(self):
        pass

    def post(self):
        try:
            startlog.info("api call hits")
            file = request.form

            base = file['Passport_Image']
            imgdata = base64.b64decode(base)
            header = file['scan_type']
            details = detect_text(base)
            startlog.info(details)
            unique_no = str(datetime.now())
            if details['type'] == 'PASSPORT':
                no = details['data']['Passport_Document_No']
                unique_no = no[5:]
            elif details['type'] == 'VISA':
                no = details['data']['Visa_Number']
                unique_no = no[5:]
          #  elif details['type']=='partial data':
          #      rand_int=random.randint(0,10000)
          #      unique_no = rand_int
            # I assume you have a way of picking unique filenames
            filename = os.path.join(
                home, 'xxxx'+str(unique_no)+'document.jpeg')
            with open(filename, 'wb') as f:
                f.write(imgdata)

            if header == 'mobile':
                crop = rotate(filename, unique_no)
                fullimage_size = ('{:,.0f}'.format(
                    os.path.getsize(filename)/float(1 << 10))+" KB")
                face = detect_faces(crop, unique_no)
                os.remove(crop)
                os.remove(filename)
            elif header == 'web':
                fullimage_size = ('{:,.0f}'.format(
                    os.path.getsize(filename)/float(1 << 10))+" KB")
                face = detect_faces(filename, unique_no)
                os.remove(filename)

            image_string = ''
            faceimage_size = ''
            if os.path.isfile(face) is True:
                with open(face, 'rb') as image:
                    image_string = base64.b64encode(image.read()).decode()
                faceimage_size = ('{:,.0f}'.format(
                    os.path.getsize(face)/float(1 << 10))+" KB")
                os.remove(face)

            logger.info("Data added successfully to passport")
            details['face'] = image_string
            details['fullimage_size'] = fullimage_size
            details['faceimage_size'] = faceimage_size
            return ({"success": True, "details": details})
        except OSError as e:
            logger.warning(traceback.format_exc())
            return ({"error": str(e), "success": False})
        except IndexError as e:
            logger.warning(traceback.format_exc())
            return ({"message": str(e), "success": False})
        except Exception as e:
            logger.warning(traceback.format_exc())
            return ({"success": False, "message": str(traceback.format_exc())})
