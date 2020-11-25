import os
import time
import sys
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

class NewRecording(Resource):
    '''
    REST API class for creation/deletion of video stream on a (part of the) screen of the raspberry.
    Create is done one by one
    Delete removes ALL video streams at once
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type = str, required = True, location = 'json')
        super(NewRecording, self).__init__()

    def post(self):
        '''
        Creates a video stream on a part of the screen
        '''
        args = self.reqparse.parse_args()
        head, tail = os.path.split(args['file'])
        file_name_parts = tail.split("_")
        ret_json = {}
        if len(file_name_parts) > 0:
            cam_name = file_name_parts[0]
            filename, file_extension = os.path.splitext(tail)
            file_extension = file_extension.replace('.', '')
            if file_extension in ['jpg', 'mp4']:
                try:
                    url = "http://"+cia+":8000/cameras/"
                    r = requests.get(url)
                    if r.status_code == 200:
                        for camera in r.json():
                            if camera['name'] == cam_name:
                                if camera['brand']['brand']['name'] == 'Reolink':
                                    ret_json = {'camera_name': cam_name, 'type': file_extension}
                except:
                    pass
        return ret_json, 201
