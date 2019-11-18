import os
import connexion
from flask import Flask
from flask_restful import Api


basedir = os.path.abspath(os.path.dirname(__file__))

connex_app =connexion.App(__name__,specification_dir='')

app = connex_app.app

api = Api(app)

cur_dir = os.getcwd()

logfolder = cur_dir+'/loggerfiles'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
STRIPE_API_KEY = 'SmFjb2IgS2FwbGFuLU1vc3MgaXMgYSBoZXJv'


def main():
    if not os.path.exists(logfolder):
        """ path doesn't exist. trying to make """
        os.makedirs(logfolder)

