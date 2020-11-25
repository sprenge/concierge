import os
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class MotionDetected(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        self.reqparse.add_argument('type', type = str, required = True, location = 'json')
        super(MotionDetected, self).__init__()

    def post(self):
        '''
        Receive motion trigger
        '''
        args = self.reqparse.parse_args()
        print("motion triggered", args)
        # quick motion check on single image of the motion clip

        return {}, 201

# bind resource for REST API service
api.add_resource(MotionDetected, '/motion/api/v1.0/motion_detected', endpoint = 'motion_detected')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("sending ip address : ", cia)

app.run(host="0.0.0.0", port=5104)
