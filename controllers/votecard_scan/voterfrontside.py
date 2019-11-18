from datetime import datetime
from flask import request
from config import basedir
from flask_restful import reqparse, Resource
import logging
import logging.config
import yaml
import base64
import os
from os.path import expanduser
from datetime import date, datetime
from exceptions import NoneType, textAnnotations
from voter_vision import detect_text
from localface import detect_faces
import random
import traceback
home = expanduser('~')

CONFIG_PATH = os.path.join(basedir, 'loggeryaml/voterlogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
logger = logging.getLogger('imagevoter')


class Votefront(Resource):

    def __init__(self):
        pass

    def post(self):
        try:
            logger.info("api call hits")
            file = request.form
            base = file['voter_image']
            doc_type = file['scanView']
            imgdata = base64.b64decode(base)
            rand_no = str(datetime.now())
            # I assume you have a way of picking unique filenames
            filename = os.path.join(home, str(rand_no)+'voterdoc.jpeg')
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
                    logger.info("face extracted")
                    details['face'] = image_string
                    details['doc_type'] = 'front'
                if 'error' in details.keys():
                    if len(details.keys()) == 1:
                        details['success'] = False
                        face_ex = {key: value for key,
                                   value in details.items() if key != 'face'}
                        logger.info(
                            "person_details_content:{}".format(face_ex))
                        return details
                    elif len(details.keys()) > 1:
                        face_ex = {key: value for key,
                                   value in details.items() if key != 'face'}
                        logger.info(face_ex)
                        return ({"success": True, "voter_details": details})
                elif 'error' not in details.keys():
                    face_ex = {key: value for key,
                               value in details.items() if key != 'face'}
                    logger.info("person_details_content:{}".format(face_ex))
                    return ({"success": True, "voter_details": details})
            elif doc_type == 'back':
                if 'error' in details.keys():
                    details['success'] = False
                    logger.info(details)
                    return details
                elif 'error' not in details.keys():
                    logger.info(details)
                    details['doc_type'] = 'back'
                    return ({"success": True, "voter_details": details})

        except IndexError as e:
            print(str(e))
            logger.warning(str(traceback.format_exc()))
            return ({"error": str(e), "success": False})
        except Exception as e:
            print(str(e))
            logger.warning(str(traceback.format_exc()))
            return ({"error": str(e), "success": False})
