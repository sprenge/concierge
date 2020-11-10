import os
import time
import sys
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("sending ip address : ", cia)

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
        print(args['file'])
        return {}, 201

# bind resource for REST API service
api.add_resource(NewRecording, '/camera/api/v1.0/reolink', endpoint = 'reolink')

if __name__ == '__main__':
    registration_not_done = True
    while (registration_not_done):
        try:
            r = requests.post("http://"+cia+":5101/ftp/api/v1.0/registerclient", 
                              json={"url": "http://"+cia+":5102/camera/api/v1.0/reolink"}, 
                              timeout=10)
            if r.status_code == 201:
                registration_not_done = False
            print(r.status_code)
        except Exception as e:
            print(e)
        time.sleep(5)
    app.run(host="0.0.0.0", port=5102)
