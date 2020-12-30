import os
import logging
import time
import pickle
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

record_ids = []
encodings = []

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
                r = requests.get("http://"+cia+":8000/rest/recordings/"+args['recording_id']+'/')
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

class CreateDeepData(Resource):
    '''

    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('record_id', type = str, required = True, location = 'json')
        super(CreateDeepData, self).__init__()

    def post(self):
        '''
        '''
        args = self.reqparse.parse_args()
        url = "http://"+cia+":8000/rest/known_objects/"+args['record_id']+'/'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                rec = r.json()
                print("rec", rec)
                if rec['object_type'] == 16:
                    cap = cv2.VideoCapture(rec['file_path_image'])
                    ret, frame = cap.read()
                    if ret:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        boxes = face_recognition.face_locations(rgb, model="hog")
                        if len(boxes) > 0:
                            log.info("face detected, create encodings {}".format(args['record_id']))
                            encodings = face_recognition.face_encodings(rgb, boxes)
                            fn = rec['file_path_image'].replace(".jpg",".enc")
                            fr = open(fn, "wb")
                            fr.write(pickle.dumps(encodings))
                            fr.close()
                            rec['deep_learning_done'] = True
                            r = requests.put(url, data=rec)
                        else:
                            log.info("no face detected remove record {}".format(args['record_id']))
                            r = requests.delete(url)
                else:
                    # not a person
                    print("create_deep_data for object")

        except Exception as e:
            log.error(str(e))

        return [], 201

class ReadKnownObjects(Resource):
    '''

    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ReadKnownObjects, self).__init__()

    def get(self):
        '''
        '''
        url = "http://"+cia+":8000/rest/known_objects/"
        try:
            r = requests.get(url)
            if r.status_code == 200:
                all_objects = r.json()
                for rec in all_objects():
                    if rec['object_type'] == 16:
                        if rec['identified']:
                            if rec['id'] not in record_ids:
                                fn = rec['file_path_image'].replace(".jpg", ".enc")
                                fr = open(fn, "rb")
                                data = fr.read()
                                fr.close()
                                encoding = pickle.loads(data)
                                encodings.append(encoding)
                                record_ids.append(rec['id'])
                                print("len record_ids", len(record_ids))

        except Exception as e:
            log.error(str(e))

api.add_resource(DeepAnalysis, '/deep_analysis/api/v1.0/get_deep_data', endpoint = 'get_deep_data')
api.add_resource(CreateDeepData, '/deep_analysis/api/v1.0/create_deep_data', endpoint = 'create_deep_data')
api.add_resource(ReadKnownObjects, '/deep_analysis/api/v1.0/read_known_objects', endpoint = 'read_known_objects')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
log.info("CONCIERGE_IP_ADDRESS %s", cia)

app.run(host="0.0.0.0", port=5106)
