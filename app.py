from controllers.driving_scan.postdriving import drivingScan
from controllers.pan_scan.pandetails import PanCardDetail
from controllers.votecard_scan.voterfrontside import Votefront
from controllers.aadhar_scan.post_aadhar import ScanAadhar
from controllers.passport.imagepost import PostImageDetail
from flask import Flask, make_response, request
import config
from config import app, cur_dir, api, main
import os
import pathlib
from flask_cors import CORS


CORS(app, resources={r"/api/*": {"origins": "*"}})


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

""" call for passport and visa"""


api.add_resource(PostImageDetail, '/api/postimagedetail')

""" call for aadhar card for front and back side"""


api.add_resource(ScanAadhar, '/api/scan_aadhar')


""" call for voterid scan for front and backside"""


api.add_resource(Votefront, '/api/voterscan')


""" call for pan card """

api.add_resource(PanCardDetail, '/api/panscan')

""" call for driving scan"""

api.add_resource(drivingScan, '/api/scandriving')


if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
