import os
import logging
import copy
import time
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import influxdb

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

shape_request_list_jpg = []
shape_request_list_mp4 = []
lock = threading.Lock()

def handle_shape_requests_jpg():
    while(1):
        shape_request = None
        lock.acquire()
        if len(shape_request_list_jpg) > 0:
            shape_request = shape_request_list_jpg.pop(0)
        lock.release()
        if shape_request:
            try:
                data = {
                    "camera_name": shape_request['camera_name'], 
                    "file": '/root'+shape_request['file'], 
                    "type": shape_request['type']
                }
                url = "http://"+cia+":5103/shape/api/v1.0/find_shape"
                r = requests.post(url, json=data, timeout=30)
                if r.status_code == 201:
                    summary_data = influxdb.summarize_analytic_data(r.json(), 'http://'+cia+':8000'+shape_request['file'], asset_type='image', motion=True)
                    if summary_data:
                        influxdb.send_recording_to_influx_db(cia, shape_request['camera_name'], summary_data, int(shape_request['epoch']))
                else:
                    log.error("expect error code 201, got %s", r.status_code)
            except Exception as e:
                log.error("%s", str(e))        
        time.sleep(0.5)

def handle_shape_requests_mp4():
    while(1):
        shape_request = None
        lock.acquire()
        if len(shape_request_list_mp4) > 0:
            shape_request = shape_request_list_mp4.pop(0)
        lock.release()
        if shape_request:
            try:
                data = {
                    "camera_name": shape_request['camera_name'], 
                    "file": '/root'+shape_request['file'], 
                    "type": shape_request['type']
                }
                url = "http://"+cia+":5105/shape/api/v1.0/find_shape"
                r = requests.post(url, json=data, timeout=1200)
                if r.status_code == 201:
                    summary_data = influxdb.summarize_analytic_data(r.json(), 'http://'+cia+':8000'+shape_request['file'], asset_type='video')
                    if summary_data:
                        influxdb.send_recording_to_influx_db(cia, shape_request['camera_name'], summary_data, int(shape_request['epoch']))
                else:
                    log.error("expect error code 201, got %s", r.status_code)
            except Exception as e:
                log.error("%s", str(e))        
        time.sleep(0.5)


class MotionDetected(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        self.reqparse.add_argument('type', type = str, required = True, location = 'json')
        self.reqparse.add_argument('epoch', type = str, required = True, location = 'json')
        super(MotionDetected, self).__init__()

    def post(self):
        '''
        Receive motion trigger
        '''
        args = self.reqparse.parse_args()
        log.debug("motion triggered %s", args)
        lock.acquire()
        shape_request_list_jpg.append(copy.deepcopy(args))
        lock.release()

        # quick motion check on single image of the motion clip

        return {}, 201

class RecordingReady(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        self.reqparse.add_argument('type', type = str, required = True, location = 'json')
        self.reqparse.add_argument('epoch', type = str, required = True, location = 'json')
        super(RecordingReady, self).__init__()

    def post(self):
        '''
        Receive recording ready trigger
        '''
        args = self.reqparse.parse_args()
        log.debug("Receive recording triggered %s", args)
        lock.acquire()
        shape_request_list_mp4.append(copy.deepcopy(args))
        lock.release()

        # quick motion check on single image of the motion clip

        return {}, 201

# bind resource for REST API service
api.add_resource(MotionDetected, '/motion/api/v1.0/motion_detected', endpoint = 'motion_detected')
api.add_resource(RecordingReady, '/motion/api/v1.0/recording_ready', endpoint = 'recording_ready')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("sending ip address : ", cia)
try:
    root_dir = os.environ['ROOT_DIR']
except:
    root_dir = ''

shape_handler_jpg = threading.Thread(target=handle_shape_requests_jpg, args=())
shape_handler_jpg.start()
shape_handler_mp4 = threading.Thread(target=handle_shape_requests_mp4, args=())
shape_handler_mp4.start()
app.run(host="0.0.0.0", port=5104)
