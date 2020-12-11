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
deep_analytics_list = []
lock = threading.Lock()

def get_desired_shapes(profile):
    '''
    Lookup the shapes configured into the database eligible for hits
    '''
    shape_set = set()
    if not profile:
        log.info("no analytics profile set")
        return shape_set
    url_profile = "http://"+cia+"/rest/analytics_profiles/"+profile
    url_shape = "http://"+cia+"/rest/analytics_shapes"
    shape_list_db = []
    try:
        r = requests.get(url_profile)
        if r.status_code == 200:
            shape_list_db = r.json()['shapes']
    except Exception as e:
        log.error(str(e))
    try:
        r = requests.get(url_shape)
        if r.status_code == 200:
            for rec in r.json():
                if rec['id'] in shape_list_db:
                    shape_set.add(rec['shape'])
    except Exception as e:
        log.error(str(e))
    return shape_set

def handle_deep_analytics():
    while(1):
        time.sleep(0.5)
        lock.acquire()
        if len(deep_analytics_list) > 0:
            record_id = deep_analytics_list.pop(0)
        lock.release()
        time.sleep(0.5)

def handle_shape_requests_jpg():
    while(1):
        shape_request = None
        lock.acquire()
        if len(shape_request_list_jpg) > 0:
            # take the next analytics request from the queue
            shape_request = shape_request_list_jpg.pop(0)
        lock.release()
        if shape_request:
            desired_shapes = get_desired_shapes(shape_request['analytics_profile'])
            if len(desired_shapes) > 0:
                try:
                    data = {
                        "camera_name": shape_request['camera_name'], 
                        "file": '/root'+shape_request['file'], 
                        "type": shape_request['type']
                    }
                    url = "http://"+cia+":5103/shape/api/v1.0/find_shape"
                    r = requests.post(url, json=data, timeout=30)
                    if r.status_code == 201:
                        influxdb.send_analytics_shape_data_to_influx(
                            cia, 
                            shape_request['camera_name'], 
                            shape_request['epoch'], 
                            r.json(), desired_shapes, 
                            )
                    else:
                        log.error("expect error code 201, got %s", r.status_code)
                except Exception as e:
                    log.error("%s", str(e))      
            else:
                log.info("No shapes to be analysed for jpg")
        time.sleep(0.5)

def handle_shape_requests_mp4():
    while(1):
        shape_request = None
        lock.acquire()
        if len(shape_request_list_mp4) > 0:
            # take the next analytics request from the queue
            shape_request = shape_request_list_mp4.pop(0)
        lock.release()
        if shape_request:
            desired_shapes = get_desired_shapes(shape_request['analytics_profile'])
            if len(desired_shapes) > 0:
                try:
                    data = {
                        "file": '/root'+shape_request['file']
                    }
                    url = "http://"+cia+":5103/shape/api/v1.0/get_video_metadata"
                    r = requests.post(url, json=data, timeout=30)
                    if r.status_code == 201:            
                        video_metadata = r.json()  
                        data = {
                            "camera_name": shape_request['camera_name'], 
                            "file": '/root'+shape_request['file'], 
                            "type": shape_request['type']
                        }
                        url = "http://"+cia+":5105/shape/api/v1.0/find_shape"
                        r = requests.post(url, json=data, timeout=1200)
                        influxdb.send_analytics_shape_data_to_influx(
                            cia, 
                            shape_request['camera_name'], 
                            shape_request['epoch'], 
                            r.json(), desired_shapes, 
                            recording_id=shape_request['id'], 
                            asset_type='video',
                            video_metadata = video_metadata)
                        lock.acquire()
                        deep_analytics_list.append(shape_request['id'])
                        lock.release()
                    else:
                        log.error("cannot get video metadata for {}".format(data['file']))

                except Exception as e:
                    log.error("%s", str(e))       
            else:
                log.info("No shapes to be analysed for mp4")
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
        self.reqparse.add_argument('analytics_profile', type = str, required = False, location = 'json')
        super(MotionDetected, self).__init__()

    def post(self):
        '''
        Receive motion trigger
        '''
        args = self.reqparse.parse_args()
        log.debug("motion triggered %s", args)
        # append request to the list for further processing
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
        self.reqparse.add_argument('analytics_profile', type = str, required = False, location = 'json')
        self.reqparse.add_argument('id', type = str, required = False, location = 'json')
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
try:
    root_dir = os.environ['ROOT_DIR']
except:
    root_dir = ''

# offload triggers for shape detection to a seperate thread
shape_handler_jpg = threading.Thread(target=handle_shape_requests_jpg, args=())
shape_handler_jpg.start()
shape_handler_mp4 = threading.Thread(target=handle_shape_requests_mp4, args=())
shape_handler_mp4.start()
deep_analytics = threading.Thread(target=handle_shape_requests_jpg, args=())
deep_analytics.start()
app.run(host="0.0.0.0", port=5104)
