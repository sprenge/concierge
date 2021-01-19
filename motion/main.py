import os
import logging
import copy
import time
import threading
import json
from os import listdir
from os.path import isfile, join
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
    confidence_level = 0.7
    min_skip_frame = 5
    max_skip_frame = 5
    if not profile:
        log.info("no analytics profile set")
        return shape_set
    url_profile = "http://"+cia+":8000/rest/analytics_profiles/"+profile
    url_shape = "http://"+cia+":8000/rest/analytics_shapes"
    shape_list_db = []
    try:
        r = requests.get(url_profile)
        if r.status_code == 200:
            shape_list_db = r.json()['shapes']
            confidence_level = r.json()['confidence_level'] / 100
            min_skip_frame = r.json()['min_nbr_video_frames_skipped']
            max_skip_frame = r.json()['max_nbr_video_frames_skipped']
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
    return min_skip_frame, max_skip_frame, shape_set, confidence_level


def handle_deep_analytics():
    while(1):
        time.sleep(0.5)
        recording_id = None
        lock.acquire()
        if len(deep_analytics_list) > 0:
            recording_id = deep_analytics_list.pop(0)
        lock.release()
        if recording_id:
            log.info("start_get_deep_data {}".format(recording_id))
            data = {}
            data['recording_id'] = str(recording_id)
            try:
                r = requests.post("http://"+cia+":5106/deep_analysis/api/v1.0/get_deep_data", json=data)
            except Exception as e:
                log.error(str(e))
            if r.status_code != 201:
                log.error("deep analytics error".format(r.status_code))
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
            log.debug("len_of_shape_request_list_mp4 {}".format(len(shape_request_list_mp4)))
            min_skip_frames, max_skip_frames, desired_shapes, confidence_level = get_desired_shapes(shape_request['analytics_profile'])
            analyse_each_n_frames = min_skip_frames
            if len(shape_request_list_mp4) > 5:
                analyse_each_n_frames = max_skip_frames
            if len(desired_shapes) > 0:
                try:
                    data = {
                        "file": '/root'+shape_request['file']
                    }
                    url = "http://"+cia+":5103/shape/api/v1.0/get_video_metadata"
                    r = requests.post(url, json=data, timeout=30)
                    if r.status_code == 201:            
                        video_metadata = r.json()
                        filename, file_extension = os.path.splitext(shape_request['file'])
                        file_base = '/root'+filename
                        data = {
                            "camera_name": shape_request['camera_name'], 
                            "file": '/root'+shape_request['file'], 
                            "type": shape_request['type'],
                            "recording_id": shape_request['id'],
                            "file_base": file_base,
                            "desired_shapes": json.dumps(list(desired_shapes)),
                            "confidence_level": confidence_level,
                            "analyse_each_n_frames": analyse_each_n_frames
                        }
                        url = "http://"+cia+":5105/shape/api/v1.0/find_shape"
                        r = requests.post(url, json=data, timeout=1200)
                        if r.status_code == 201:
                            shape_list = r.json()
                            influxdb.send_analytics_shape_data_to_influx(
                                cia, 
                                shape_request['camera_name'], 
                                shape_request['epoch'], 
                                shape_list, desired_shapes, 
                                recording_id=shape_request['id'], 
                                asset_type='video',
                                video_metadata = video_metadata)
                            for shape_entry in shape_list:
                                rec = {"camera_name": shape_request['camera_name']}
                                rec['shape_type'] = shape_entry['shape']
                                rec['snapshot_url'] = shape_entry['snapshot_url']
                                rec['time'] = 'tbd'
                                r = requests.post('http://'+cia+':5107/interworking/api/v1.0/register_detected_shape', json=rec)
                                if r.status_code != 201:
                                    log.error("register_detected_shape error {}".format(r.status_code))
                            lock.acquire()
                            deep_analytics_list.append(shape_request['id'])
                            lock.release()
                        else:
                            log.error("find_shape error code {}".format(r.status_code))
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
        self.reqparse.add_argument('file', type = str, required = True, location = 'json')
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
        
        # TBC Report motion detection to interworking

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
shape_handler_mp4 = threading.Thread(target=handle_shape_requests_mp4, args=())
shape_handler_mp4.start()
deep_analytics = threading.Thread(target=handle_deep_analytics, args=())
deep_analytics.start()
app.run(host="0.0.0.0", port=5104)
