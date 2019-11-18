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
import traceback
from config import basedir
import logging
import logging.config
import yaml

CONFIG_PATH = os.path.join(basedir, 'loggeryaml/voterlogger.yaml')
logging.config.dictConfig(yaml.safe_load(open(CONFIG_PATH)))
logger = logging.getLogger('imagevoter')


def detect_text(image_file, doc_type):
    try:
        gender_list = ['MALE', 'FEMALE', 'Male', 'Female']
        ignore_list = ['ELECTION ', 'ELECTION COMMISSION OF', 'S NAME', 'EECTOR PHOTO IDENTITY', 'ELECTOR',     'IDENTITY CARD',
                       'IDENTITY CAR', 'Date of Birth', 's Name', 'HI FAM', 'OF INDIA', 'INDIA ', 'INDIA PD', 's Name', 'Date of Birtta', 'IDENTITY CARD']

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
        block = str(text).split('\n')
        if doc_type == 'front':
            for y in block:
                removesymbol = re.search(r'([a-zA-Z0-9]+)', y)
                if removesymbol is None:
                    block.remove(y)

            for x in block:
                if x == 'Name:':
                    block.remove(x)
            base = re.compile(
                '([a-zA-Z]{3}[0-9]{7}|[a-zA-Z]{3}[0-9]+|[a-zA-Z]{2}\/[0-9]{2}\/[0-9]{3}\/[0-9]{1,6})')
            data = base.findall(text)

            data = [x for x in data if len(x) > 5]
            regex = re.compile(
                '(Age as on|Photo|hoto 10|er a 6|on Pv6|Age as on )')
            data = ([regex.sub('', i) for i in data])
            id = ''
            if len(data) >= 1:
                for x in data:
                    if len(x) >= 5:
                        if 'XXXX' not in x:
                            id = x
                            break
            else:
                id = ''
            sex = ''
            for x in block:
                for y in gender_list:
                    if y in x:
                        sex = y
            noun = re.compile(
                '([a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+)')
            name = noun.findall(text)
            for x in ignore_list:
                r = re.compile(x)
                if list(filter(r.match, name)):
                    match = list(filter(r.match, name))
                    if match[0]:
                        listmatch = match[0]
                        pop_dob = name.index(listmatch)
                        name.pop(pop_dob)
            for y in name:
                if y in ignore_list:
                    pop_dob = name.index(y)
                    name.pop(pop_dob)
            likes = ['.*ELECTION.* ', '.*Election Commission of.*', '.*Duplicate.*', '.*IIII.*', '.* Photo.*', '.*COMMISSION .*', '.*EPIC.*', '.*XIZ.*', '.*care.*', '.*card.*', '.*water.*', '.*ELECTION COMMISSION OF.*', '.*S NAME.*', '.*Age.*', '.*Eeron.*', '.*EECTOR PHOTO IDENTITY.*',
                     'ELECTOR',     '.*IDENTITY CARD.*', '.*IDENTITY.*', '.*Date of Birth.*', '.*s Name.*', '.*HI FAM.*', '.*OF INDIA.*', '.*INDIA.* ', '.*INDIA PD.*', '.*s Name.*', '.*Date of Birtta.*', '.*IDENTITY CARD.*']
            dob_in = re.compile(
                '[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}|[0-9]{2}\/[0-9]{2}\/[0-9]+|[a-zA-Z]{2}\/[a-zA-Z]{2}\/[0-9]+')
            date = dob_in.findall(text)
            date_of_birth = ''
            if len(date) >= 1:
                date_of_birth = date[0]

            for x in likes:
                r = re.compile(x)
                if list(filter(r.match, name)):
                    match = list(filter(r.match, name))
                    if match[0]:
                        listmatch = match[0]
                        pop_dob = name.index(listmatch)
                        name.pop(pop_dob)

            person_name = ''
            if len(name) >= 1:

                regex = re.compile(
                    '([^a-zA-Z0-9-/ ]|\d+|\-|I L AJ|DATE OF BIRTH|HI FAM|SPIC EN|EPALLI|Mother|Name |Father|Duplicate|EPISO|SAREE|HANDMADE|LADESH PADA|ESH ANDR E SE|Name:|NAME|EPIC|SERIES|IDENTITY CARD|HUSBAND|S NAME|card|ELECTOR|Elector|s Name|Husband|Smt|FATHER|Election Commission of|PICES|DUPLATE)')
                name = ([regex.sub('', i) for i in name])
                name = [x.lstrip(' ') for x in name if x !=
                        '' if x != '  ' if x != '   ' if x != ' ' if len(x) >= 4]
                if len(name) >= 1:

                    person_name = name[0]

            if id != '':
                for x in block:
                    abc = re.search(str(id), x)
                    if abc:
                        index_match = block.index(x)
                after_removeid = block[index_match+1:]

                regex = re.compile(
                    '([^a-zA-Z0-9-/ ]|\d+|\-|HI FAM|AMERIC|SPIC EN|pre E|TRENICS|OR RAJ|EPALLI|Mother|Name |ipornpapers|Father|Duplicate|EPISO|SAREE|HANDMADE|LADESH PADA|ESH ANDR E SE|Name:|NAME|EPIC|SERIES|IDENTITY CARD|HUSBAND|S NAME|card|ELECTOR|Elector|s Name|Husband|Smt|FATHER|Election Commission of|PICES|DUPLATE)')
                after_removeid = ([regex.sub('', i) for i in after_removeid])
                after_removeid = [x.lstrip(' ') for x in after_removeid if x !=
                                  '' if x != '  ' if x != '   ' if x != ' ' if x != 'EE EN' if len(x) >= 4]
                after_removeid = [x.rstrip(' ') for x in after_removeid]
                after_removeid = [x for x in after_removeid if len(x) > 4]

                person_name = after_removeid[0]

            person_details = {"uid": id, "name": person_name,
                              "sex": sex, "Date_of_birth": date_of_birth}

            return person_details
        elif doc_type == 'back':
            for x in block:
                if 'ADDRESS' in x:
                    abc = block.index(x)
                elif 'Address' in x:
                    abc = block.index(x)
                elif 'Addres' in x:
                    abc = block.index(x)
                elif 'Addre' in x:
                    abc = block.index(x)
            date_of_birth = ''
            for x in block[:abc]:
                find_date = re.compile(r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})')
                date_find = find_date.findall(x)
                if len(date_find) == 1:
                    date_of_birth = date_find[0]
            final = block[abc:]
            regex = re.compile(
                '([^a-zA-Z0-9-/ ]|Address|Addres|Addre|ADDRESS)')
            final = ([regex.sub('', i) for i in final])
            last = ''
            for x in final:

                if 'Date' in x:
                    last = final.index(x)
            if last != '':
                final_address = final[:last]
            else:
                add_length = (len(final))//2
                final_address = final[:add_length+5]
            final_address = [x for x in final_address if x !=
                             '' if 'ELECT' not in x if len(x) > 3]
            date_index = ''
            if len(final_address) > 10:
                for x in final_address:
                    abc = re.search(r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})', x)
                    if abc:
                        date_index = final_address.index(x)

            if date_index != '':
                final_address = final_address[:date_index]
            extra_index = ''
            if len(final_address) > 1:
                for x in final_address:
                    abc = re.search(r'Electoral|Facsimile|Assembly', x)
                    if abc:
                        extra_index = final_address.index(x)
            if extra_index != '':
                final_address = final_address[:extra_index]
            address = ' '.join(x for x in final_address)

            address = re.sub(
                '[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|[a-zA-Z]{3}[0-9]{7}|/Locality|Village|Pin|Code|Date|Scanned|Resten|lector|Registration|Officer|Facsimile', '', address)
            final_address = address.split()
            pincode = re.findall(r'[0-9]{6}', address)

            if len(pincode) > 0:
                for x in final_address:
                    pin = re.search('([0-9]{6})', x)
                    if pin:
                        final_address.remove(x)
                final_address.append(pincode[0])

            final_address = [x.rstrip(' ') for x in final_address]

            final_address = [
                x.lstrip(' ') for x in final_address if 'Signature' not in x if x != 'Eal' if x != 'of' if x != '/']
            person_address = ' '.join(x for x in final_address)
            pin_get = re.findall('[0-9]{6}', person_address)
            postal_code = ''
            state = ''
            try:
                if len(pin_get) > 0:
                    pin_code = requests.get(
                        "https://api.postalpincode.in/pincode/"+str(pin_get[0])).json()
                    if pin_code[0]['Status'] == 'Success':

                        postal_code = pin_get[0]
                        state = pin_code[0]['PostOffice'][0]['State']
                    elif pin_code[0]['Status'] == 'Error':
                        person_address = re.sub(
                            '[0-9]{6}', '', person_address)
            except:
                postal_code = ''
                state = ''
            return {"person_address": person_address, "Date_of_birth": date_of_birth, "postal_code": postal_code, "state": state}
    except IndexError as e:
        logger.warning(str(traceback.format_exc()))
        return ({"error": str(e)})
    except Exception as e:
        logger.warning(str(traceback.format_exc()))
        return ({"error": str(e)})
