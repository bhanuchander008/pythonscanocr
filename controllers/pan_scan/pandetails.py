from datetime import datetime
from flask import request
from flask_restful import reqparse, Resource
import logging
import logging.config
import yaml
import base64
from face_detect import detect_faces
import os
from os.path import expanduser
from config import basedir
from datetime import date, datetime
from exceptions import NoneType, textAnnotations
from pancard import detect_text

home = expanduser('~')
time = datetime.now().time()
CONFIG_PATH = os.path.join(basedir, 'loggeryaml/passportlogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
consolelog = logging.getLogger('pancarddetails')


class PanCardDetail(Resource):
    def __init__(self):
        pass

    def post(self):
        try:
            consolelog.info("api call hits")
            base_data = request.form.to_dict()
            imagedata = base64.b64decode(base_data['pancard'])
            # I assume you have a way of picking unique filenames
            filename = os.path.join(home, 'xxxx'+str(time)+'document.jpeg')
            with open(filename, 'wb') as f:
                f.write(imagedata)
            details = detect_text(filename)
            consolelog.info("details extracted")
            os.remove(filename)
            return ({"success": True, "details": details})
        except IndexError as e:
            consolelog.warning(str(e))
            return ({"error": str(e), "success": False})
        except Exception as e:
            consolelog.warning(str(e))
            return ({"success": False, "message": str(e)})
