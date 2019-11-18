import base64
import requests
import io
import os
import json
import re
from os.path import join
from difflib import get_close_matches
import dateparser
from collections import defaultdict, OrderedDict
import logging
import logging.config
import yaml
import traceback
from config import basedir

CONFIG_PATH = os.path.join(basedir, 'loggeryaml/drivinglogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
logger = logging.getLogger('post_licence')


def detect_text(image_file):
    try:
        url = 'https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAOztXTencncNtoRENa1E3I0jdgTR7IfL0'
        header = {'Content-Type': 'application/json'}
        body = {
            'requests': [{
                'image': {
                    'content': image_file,
                },
                'features': [{
                    'type': 'DOCUMENT_TEXT_DETECTION',
                    'maxResults': 100,
                }],
                "imageContext": {
                    "languageHints": ["en-t-iO-handwrit"]
                }
            }]
        }

        response = requests.post(url, headers=header, json=body).json()
        text = response['responses'][0]['textAnnotations'][0]['description'] if len(
            response['responses'][0]) > 0 else ''

        text = re.sub('_', ' ', text)
        block = str(text).split('\n')
        block =[x for x in block if 'Form 7' not in x]
        
        dates = re.findall(
            '(\d{2}\/\d{2}\/\d{4}|\d{2}\-\d{2}\-\d{4}|[0-9]{1,2}\-[A-Za-z]{3}\-[0-9]{2,4}|[0-9]{1,2} [A-Z0-9]{1,3} [0-9]{4})', text)

        abc = len(dates)
        Date_of_birth = ''
        if abc > 0:
            get_date = [dates[i][6:10] for i in range(abc)]

            min_year = min(get_date)
            max_year = max(get_date)
            for x in list(set(dates)):
                if max_year in x:
                    expiryDate = x

                elif min_year in x:
                    Date_of_birth = x

                else:
                    date_of_issue = x

        no=re.findall('([A-Z]{2,6} [0-9]{4}\-[0-9]{5,7}|[A-Z]{2,6}\-[0-9]{2,6}\-[0-9]{2,6}|[A-Z]{1,3}\-[0-9]{3,5}\/[0-9]{5,7}|[A-Z0-9]{2,6} [0-9]{5,13}|[A-Z0-9]{2,5}\/[0-9]{2,6}\/[0-9]{1,4}\/[0-9]{1,4}\/[0-9]{1,4}|[A-Z0-9]{14,18}|[A-Z0-9]{3,5} [0-9]{2,4} [0-9]{7}|[A-Z0-9]{3,5}\-[0-9]{2,4}\-[0-9]{7}|[A-Z]{2}\-[0-9]{2}\/[0-9]{3,5}\/[0-9]{7}|[0-9]{1,2}\/[0-9]{3,4}\/[0-9]{4}|[A-Z]{1,2}\/[A-Z]{1,2}\/[0-9]{1,4}\/[0-9]{5,7}\/[0-9]{4}|[A-Z]{2,6}\-[0-9]{9,15}|[A-Z- ]{2,6}[0-9]{4,15}|[A-Z]{2}[0-9]{2}\/[A-Z]{3}\/[0-9]{5}\-[0-9]{2}\/[0-9]{4}|[A-Z]{1,2}\/[A-Z]{2}\/[0-9]{10}\/[0-9]{4}|[A-Z]{2}\-[0-9]{2} [0-9]{11}|[0-9]{4}\/[0-9]{4}|[A-Z]{2} [0-9]{2}\/[A-Z]{3}\/[0-9]{2}\/[0-9]{5})',text)
        uid =''
        try:
            try:
                if len(no)>0:
                  
                    licence_no = [x for x in no if len(x)>=10]
                    
                    if re.search('\d',licence_no[0]) is not None:
                        uid=licence_no[0] 

            
            except:
                
                no = [x for x in no if re.search('[0-9]{4}\/[0-9]{4}',x)]
                
                uid=no[0]
        except:
            uid =''
        address = []
        for x in block:
            if 'Address' in x or 'ADDRESS' in x or 'Address :' in x or 'Add ' in x or 'Addess' in x or 'ADORESS' in x:
                abc = block.index(x)

                address = block[abc:]
                break
        person_address = ''
        if len(address) > 0:
            for x in address:
                if re.search('([0-9]{6}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|Holder|Issuing|Sign|licenced|Signature)', x):
                    ind = address.index(x)
                    final_address = address[:ind+1]
                    person_address = ' '.join(x for x in final_address)
                    person_address = re.sub(
                        '[^A-Za-z0-9-/ ]', '', person_address)
                    
                    break
        if person_address != '':
            final_address = person_address.split()
            for x in final_address:
                if re.search('([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|Holder|Issuing|Signature|licenced)', x):
                    ind = final_address.index(x)
                    final_address = final_address[:ind]
                    person_address = ' '.join(x for x in final_address)
                    
                    break
        elif person_address == '':
            for x in block:
                if x.startswith('AP') or x.startswith('TS') or x.startswith('DLFAP'):
                    abc = block.index(x)

                    address = block[abc+3:]
                    
            if len(address) > 0:
                for x in address:
                    if re.search('([0-9]{6}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|Holder|Issued|Sign|Signature|licenced)', x):
                        ind = address.index(x)
                        final_address = address[:ind+1]
                        person_address = ' '.join(x for x in final_address)
                        person_address = re.sub(
                            '[^A-Za-z0-9-/ ]|[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}', '', person_address)
                        
                        break
        
        name = ''
        for x in block:
            if 'Name' in x or 'NAME' in x or 'Nam ' in x:
                abc = block.index(x)

                noun = block[abc]
                name = re.sub('[^A-Za-z]|Name|NAME|Nam|ATH ', '', noun)

                if name == '':

                    name = re.sub('DOB|D.O.B|-|/', '', block[abc+1])

                    if re.search('\d', name) is not None:
                        name = block[abc+2]

                        break
                break
        if name!='':
            if re.search('Designation|Original|RTA|[0-9]+',name):
                
                name = ''
  
        if name == '':
            for x in block:
                if 'S/D/W of'in x:
                    abc = block.index(x)

                    noun = block[abc-1]
                    name = noun
        if name == '':
            for x in block:
                if x.startswith('AP') or x.startswith('TS') or x.startswith('DLFAP'):
                    abc = block.index(x)

                    noun = block[abc+1]
                    name = noun
        if name!='':
            if re.search('Designation|Original|RTA|[0-9]+|Slo',name):
                name = ''

        if person_address !='':
            pin_get=re.findall('[0-9]{6}',person_address)
            person_address=re.sub('Permanent|Signature','',person_address)
           
            person_address =re.sub('/Address|/Addess|/Ad|/ Address|/ Addess|/ Ad|Add|/Add|Addess|Ad','Address',person_address)
            person_address=re.sub('PIN','',person_address)
            final_address=person_address.split()
            final_address= list(OrderedDict((element, None) for element in final_address))
            if len(pin_get) > 0:
                for x in final_address:
                    abc=re.search('([0-9]{6})',x)
                    if abc:
                        no_pin=final_address.index(x)
                        final_address=final_address[:no_pin]
                final_address.append(pin_get[0])
                person_address=' '.join(x for x in final_address)
                
        if person_address!='':
             person_address=re.sub('Issued on|Issued|Date of First Issue|ssued|DoB|[0-9]{2}\/[0-9]{2}\/[0-9]{4}','',person_address)
        postal_code = ''
        state = ''
        try:
            if len(pin_get)>0:
                
                pin_code=requests.get("https://api.postalpincode.in/pincode/"+str(pin_get[0])).json()
                if pin_code[0]['Status']=='Success':
                    postal_code=pin_get[0]
                    state = pin_code[0]['PostOffice'][0]['State']
                elif pin_code[0]['Status']=='Error':
                    person_address = re.sub(
                                '[0-9]{6}', '', person_address)
        except:
            postal_code = ''
            state = ''

        details = {"uid": uid, "Date_of_birth": Date_of_birth,
                   "name": name, "person_address": person_address,"state":state,"postal_code":postal_code}

        return details
    except Exception as e:
        logger.warning(str(traceback.format_exc()))
        return ({"error": str(e)})
