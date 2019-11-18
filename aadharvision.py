import base64
import requests
import io
import os
import json
import re
import datetime
from datetime import date
from os.path import join
from collections import defaultdict, OrderedDict
from difflib import get_close_matches
import dateparser
import traceback
from config import basedir
import logging
import logging.config
import yaml

CONFIG_PATH = os.path.join(basedir, 'loggeryaml/aadharlogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
logger = logging.getLogger('post_aadhar')


def detect_text(image_file, doc_type):
    try:
        remove=['GOVERNMENT OF INDIA','Government of India','Year of Birth','/ Male','GOVERNMENT OF IND','Nent of India','GOVERMENTER']
        unlike=['UNIQUE IDENTIFICATION AUTHORITY','OF INDIA','Identification','Bengaluru-560001','-500001','500001','Bengaluru-580001','560001',' WWW','WWW','-560001','-560101','560101','uidai','Aam Admi ka','VvV','he','uldai','uldal','govin','www','A Unique Identification','Www','in','gov','of India','uidai','INDIA','India','www','I','1B 1ST','MERI PEHACHAN','1E 1B','MERA AADHAAR','Unique Identification Authority','of India','UNQUE IDENTIFICATION AUTHORITY','1800 180 1947','1800180 1947','Admi ka Adhikar','w','ww','S','s','1800 180 17','WWW','dai','uidai','Address','1809 180 1947','help','AADHAAR','160 160 1947','Aadhaar','180 18167','Aadhaar-Aam Admi ka Adhikar','gov in','1947','MERA AADHAAR MERI PEHACHAN','38059606 3964','8587 1936 9174','Unique Identification Authority of India']
       
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
        text = response['responses'][0]['textAnnotations'][0]['description'] if len(response['responses'][0]) > 0 else ''

        block=str(text).split('\n')
        if doc_type=='front':
            abc=[str(x) for x in block]
            dob_in=re.compile('[0-9]{4}|[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}')
            date=dob_in.findall(text)
            date_of_birth = date[0]
            for y in date:
                find_date = re.search(r'([0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4})',y)
                if find_date:
                    date_of_birth = y
            #parsed_birth=dateparser.parse(date[0],settings={'DATE_ORDER': 'YMD'}).date()
            gender_list = ['MALE', 'FEMALE', 'Male', 'Female']
            gender = ''
            for x in block:
                for y in gender_list:
                    if y in x:
                        gender = y
                        print("getting gender:", y)
            da_find = re.compile(
                '([0-9]{2,4} [0-9]{2,4} [0-9]{2,4}|[0-9]+ [0-9]+|[0-9]{12})')
            number = da_find.findall(text)
            number = [x for x in number if len(x) > 6]
            uid = number[0]
            for x in number:
                find_uid = re.search(r'([0-9]+ [0-9]+ [0-9]+)', x)
                if find_uid:
                    uid = x
            uid_number = re.sub(' ','',uid)
            print(uid_number,"uid_number")
            if len(uid_number)!=12:
                uid= ''
            print("uid:",number)
            if date_of_birth in uid:
                date_of_birth =''
            na_find=re.compile('([a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+)')
            noun=na_find.findall(text)
            print(noun)
            noun = [x for x in noun if x not in remove if 'GOVERNMENT' not in x if 'Government' not in x if 'Govern' not in x if 'GOVERN' not in x if 'Gove' not in x if 'GOVE' not in x if 'ERNMENT' not in x if 'ernment' not in x]
            person_details={"Date_of_birth":date_of_birth,"sex":gender,"uid":uid,"name":noun[0]}
            return person_details
        elif doc_type == 'back':
            final_address = []
            for x in block:
                if 'Address' in x:
                    abc = block.index(x)
            address = block[abc:]
            regex = re.compile('([^a-zA-Z0-9-/ ]|Address|No|www|o  |uidai)')
            cannot = ([regex.sub('', i) for i in address])
            cannot = [x for x in cannot if x not in unlike]
            unique_list = list(OrderedDict((element, None)
                                           for element in cannot))
            for x in unique_list:
                abc = x.lstrip('  ')
                abc = x.lstrip(' -')
                abc = x.lstrip(' ')
                final_address.append(abc)
            for x in final_address:
                match = re.compile('(govin|ligovin|help)')
                abc = match.search(x)
                if abc:
                    index_match = final_address.index(x)
                    final_address.remove(x)
            for x in final_address:
                pin = re.search('([0-9]{6})', x)
                if pin:
                    ind = final_address.index(x)
            final_address = final_address[:ind+1]
            abc = ' '.join(x for x in final_address)
            final = abc.split()
            final_address= list(OrderedDict((element, None) for element in final))
            person_address=' '.join(x for x in final_address)
            pin_code = re.findall('([0-9]{6})',person_address)
            for x in final_address:
                abc=re.search('([0-9]{6})',x)
                if abc:
                    final_address.remove(x)
            final_address.append(pin_code[0])
            person_address=' '.join(x for x in final_address)
            pin_get=re.findall('[0-9]{6}',person_address)
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
            return {'person_address':person_address,"postal_code":postal_code,"state":state}
    except IndexError as e:
        logger.warning(str(traceback.format_exc()))
        return ({"error": str(e)})
    except Exception as e:
        logger.warning(str(traceback.format_exc()))
        return ({"error": str(e)})
