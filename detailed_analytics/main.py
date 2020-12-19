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

def analyse_person(shape, cap):
    '''
    Look for face shape
    '''
    print("shape", shape)
    cap.set(cv2.CAP_PROP_POS_FRAMES,int(shape['frame_nbr']))
    ret, frame = cap.read()
    if ret:
        startX = int(shape['startX'])
        endX = int(shape['endX'])
        startY= int(shape['startY'])
        endY = int(shape['endY'])
        crop_img = frame[startY:endY, startX:endX]
        rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="hog")
        for top, right, bottom, left in boxes:
            # fn = '/root/static/tmp/'+str(int(time.time()*1000000))+'.jpg'
            # cv2.rectangle(crop_img, (left, top), (right, bottom), (255,0,0), 2)
            # cv2.imwrite(fn, crop_img)
            print("found face", top, right, bottom, left)
        pass

class DeepAnalysis(Resource):
    '''
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('recording_id', type = str, required = False, location = 'json')
        super(DeepAnalysis, self).__init__()

    def post(self):
        '''
        '''
        args = self.reqparse.parse_args()
        recording_data = {}
        try:
            r = requests.get("http://"+cia+":5107/interworking/api/v1.0/shapes_video/"+args['recording_id'])
        except Exception as e:
            log.error(str(e))
        if r.status_code == 200:
            shape_list = r.json()
            try:
                r = requests.get("http://"+cia+":80/rest/recordings/"+args['recording_id']+'/')
                if r.status_code == 200:
                    recording_data = r.json()
                    cap = cv2.VideoCapture('/root'+recording_data['file_path_video'])
                    for shape in shape_list:
                        if shape['shape'] == 'person':
                            analyse_person(shape, cap)
                else:
                    log.error("error get recording data from rest interfafe{}".format(r.status_code))
            except Exception as e:
                log.error(str(e))
            cap = cv2.VideoCapture('/root'+recording_data['file_path_video'])
            for shape in shape_list:
                if shape['shape'] == 'person':
                    analyse_person(shape, cap)

        else:
            log.error("deep analytics error".format(r.status_code))

        return shape_list, 201

api.add_resource(DeepAnalysis, '/deep_analysis/api/v1.0/get_deep_data', endpoint = 'get_deep_data')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
log.info("CONCIERGE_IP_ADDRESS %s", cia)

app.run(host="0.0.0.0", port=5106)
