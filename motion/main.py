import os
import copy
import time
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

shape_request_list = []
lock = threading.Lock()

def handle_shape_requests():
    while(1):
        shape_request = None
        lock.acquire()
        if len(shape_request_list) > 0:
            shape_request = shape_request_list.pop(0)
            print("shape_request1", shape_request)
        lock.release()
        if shape_request:
            try:
                data = {"camera_name": shape_request['camera_name'], "file": '/root'+shape_request['file']}
                url = "http://"+cia+":5103/shape/api/v1.0/find_shape"
                print("find shape url", url)
                r = requests.post(url, json=data, timeout=5)
            except Exception as e:
                print(e)        
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
        super(MotionDetected, self).__init__()

    def post(self):
        '''
        Receive motion trigger
        '''
        args = self.reqparse.parse_args()
        print("motion triggered", args)
        lock.acquire()
        shape_request_list.append(copy.deepcopy(args))
        lock.release()

        # quick motion check on single image of the motion clip

        return {}, 201

# bind resource for REST API service
api.add_resource(MotionDetected, '/motion/api/v1.0/motion_detected', endpoint = 'motion_detected')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("sending ip address : ", cia)
try:
    root_dir = os.environ['ROOT_DIR']
except:
    root_dir = ''
print("root_dir : ", root_dir)

shape_handler = threading.Thread(target=handle_shape_requests, args=())
shape_handler.start()
app.run(host="0.0.0.0", port=5104)
