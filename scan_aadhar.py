from PIL import Image
from pyzbar.pyzbar import decode
import re
import xmltodict

def qr_scan(img_path):
    aadhar_details={}
    data = decode(Image.open(img_path))
    qr_extracted_data=(data[0][0]).decode("utf-8")
    person_address=[]
    address=[]
    if '"UTF-8"?>\n' in qr_extracted_data:
        d=(xmltodict.parse(qr_extracted_data,process_namespaces=True))
        original=d['PrintLetterBarcodeData']
        person_data=dict(original)
        print(person_data)
        data = {key.lstrip('@'):value   for key,value in person_data.items()}
        #print("dnlflgn:",data)
        for key,value in data.items():
            if key not in ['name','uid','yob','dob','gender']:
                if value!='':
                    person_address.append(value)
        #print("person_address:",person_address)
        address.append(data['co'])
        address.append(data['house'])
        if 'loc' in data.keys():
            address.append(data['loc'])
        if 'street' in data.keys():
            address.append(data['street'])
        address.append(data['vtc'])
        if 'subdist' in data.keys():
            address.append(data['subdist'])
        address.append(data['dist'])
        address.append(data['state'])
        address.append(data['pc'])
        aadhar_details['name'] = data['name']
        if 'dob' in data.keys():
            aadhar_details['date of birth'] = data['dob']
        else:
            aadhar_details['date of birth'] = ' '
        aadhar_details['year of birth']=data['yob']
        aadhar_details['uid']=data['uid']
        aadhar_details['gender']=data['gender']
        aadhar_details['address']=address
        return aadhar_details
    elif '"UTF-8"?> <' in qr_extracted_data:
        rply = qr_extracted_data.replace('UTF-8?">','UTF-8"?>\n')

        d=(xmltodict.parse(rply,process_namespaces=True))
        original=d['PrintLetterBarcodeData']
        person_data=dict(original)
        #print("data_json:",person_data)
        data = {key.lstrip('@'):value   for key,value in person_data.items()}
        for key,value in data.items():
            if key not in ['name','uid','yob','dob','gender']:
                if value!='':
                    person_address.append(value)

        #print("person_address:",person_address)
        address.append(data['co'])
        address.append(data['house'])
        if 'loc' in data.keys():
            address.append(data['loc'])
        if 'street' in data.keys():
            address.append(data['street'])
        address.append(data['vtc'])
        if 'subdist' in data.keys():
            address.append(data['subdist'])
        address.append(data['dist'])
        address.append(data['state'])
        address.append(data['pc'])
        aadhar_details['name'] = data['name']
        if 'dob' in data.keys():
            aadhar_details['date of birth'] = data['dob']
        else:
            aadhar_details['date of birth'] = ' '
        aadhar_details['year of birth'] = data['yob']
        aadhar_details['uid']=data['uid']
        aadhar_details['gender']=data['gender']
        aadhar_details['address']=address
        return aadhar_details
    elif '"utf-8?"><' in qr_extracted_data:
        rply = qr_extracted_data.replace('utf-8?">','utf-8"?>\n')
        d=(xmltodict.parse(rply,process_namespaces=True))
        original=d['PrintLetterBarcodeData']
        person_data=dict(original)
        print("person_data:",person_data)
        data = {key.lstrip('@'):value   for key,value in person_data.items()}
        for key,value in data.items():
            if key not in ['name','uid','yob','dob','gender']:
                if value!='':
                    person_address.append(value)
        #print("person_address:",person_address)
        address.append(data['co'])
        if 'house' in data.keys():
            address.append(data['house'])
        if 'loc' in data.keys():
            address.append(data['loc'])
        if 'street' in data.keys():
            address.append(data['street'])
        address.append(data['vtc'])
        if 'subdist' in data.keys():
            address.append(data['subdist'])

        address.append(data['dist'])
        address.append(data['state'])
        address.append(data['pc'])
        aadhar_details['name'] = data['name']
        if 'dob' in data.keys():
            aadhar_details['date of birth'] = data['dob']
        else:
            aadhar_details['date of birth'] = ' '
        aadhar_details['year of birth'] = data['yob']
        aadhar_details['uid']=data['uid']
        aadhar_details['gender']=data['gender']
        aadhar_details['address']=address
        return aadhar_details

