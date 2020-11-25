import os
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class FindShape(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        super(FindShape, self).__init__()

    def post(self):
        '''
        Receive request to find shapes in an image file or video file
        Supports two file formats (file suffixes) : jpg and mp4
        '''
        args = self.reqparse.parse_args()
        print("find shape trigger", args)
        # quick motion check on single image of the motion clip
        return {}, 201

# bind resource for REST API service
api.add_resource(FindShape, '/shape/api/v1.0/find_shape', endpoint = 'find_shape')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("sending ip address : ", cia)

app.run(host="0.0.0.0", port=5104)
