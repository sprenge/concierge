import os
import logging
import time
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import cv2
import numpy as np
import face_recognition

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

app = Flask(__name__)
api = Api(app)

def analyse_person():
    pass

class DeepAnalysis(Resource):
    '''
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('record_id', type = str, required = False, location = 'json')
        super(DeepAnalysis, self).__init__()

    def post(self):
        '''
        '''
        args = self.reqparse.parse_args()

        cap = cv2.VideoCapture(args['file'])


        return shape_list, 201

api.add_resource(DeepAnalysis, '/deep_analysis/api/v1.0/get_deep_data', endpoint = 'get_deep_data')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
log.info("CONCIERGE_IP_ADDRESS %s", cia)

app.run(host="0.0.0.0", port=5106)
