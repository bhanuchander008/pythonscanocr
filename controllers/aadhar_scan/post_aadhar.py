from flask import request
from config import basedir
from flask_restful import reqparse, Resource
import os
import logging
import logging.config
import yaml
import base64
from os.path import expanduser
from datetime import date, datetime
from localface import detect_faces
from aadharvision import detect_text
import random
home = expanduser('~')

date = str(date.today())


CONFIG_PATH = os.path.join(basedir, 'loggeryaml/aadharlogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
logger = logging.getLogger('post_aadhar')


class ScanAadhar(Resource):

    def __init__(self):
        pass

    def post(self):
        try:
            file = request.form
            base = file['aadhar_image']
            doc_type = file['scanView']
            imgdata = base64.b64decode(base)
            rand_no = str(datetime.now())
            # I assume you have a way of picking unique filenames
            filename = os.path.join(home, str(rand_no)+'aadhardoc.jpeg')
            with open(filename, 'wb') as f:
                f.write(imgdata)
            details = ''
            details = detect_text(base, doc_type)
            logger.info(details)
            image_string = ' '
            rand_int = str(datetime.now())
            face = detect_faces(filename, rand_int)
            os.remove(filename)
            if doc_type == 'front':
                if os.path.isfile(face) is True:
                    with open(face, 'rb') as image:
                        image_string = base64.b64encode(image.read()).decode()
                    faceimage_size = ('{:,.0f}'.format(
                        os.path.getsize(face)/float(1 << 10))+" KB")
                    os.remove(face)
                    logger.info(details)
                    details['face'] = image_string
                    details['doc_type'] = 'front'
                if 'error' in details.keys():
                    if len(details.keys()) == 1:
                        details['success'] = False
                        logger.info(details)
                        return details
                    elif len(details.keys()) > 1:
                        logger.info(details)
                        return ({"success": True, "aadhar_details": details})
                elif 'error' not in details.keys():
                    return ({"success": True, "aadhar_details": details})
            elif doc_type == 'back':
                if 'error' in details.keys():
                    details['success'] = False
                    logger.info(details)
                    return details
                elif 'error' not in details.keys():
                    details['doc_type'] = 'back'
                    return ({"success": True, "aadhar_details": details})

        except IndexError as e:
            logger.warning(str(e))
            return ({"error": str(e), "success": False})
        except Exception as e:
            logger.warning(str(e))
            return ({"error": str(e), "success": False})
