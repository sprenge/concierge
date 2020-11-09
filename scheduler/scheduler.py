import os
import time
import sys
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class Scheduler(Resource):
    '''
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type = str, required = True, location = 'json')
        super(Scheduler, self).__init__()

    def post(self):
        '''
        Creates a video stream on a part of the screen
        '''
        args = self.reqparse.parse_args()
        print(args['file'])
        return {}, 201

    def delete(self):
        '''
        '''
        return {}, 201

# bind resource for REST API service
api.add_resource(Scheduler, '/ftp/api/v1.0/files', endpoint = 'files')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5100)
