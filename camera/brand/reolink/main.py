''' Reo link specific code for handling recording and configuration requests 
'''
import os
import time
import logging
import sys
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from recording import NewRecording
import reoconfig

app = Flask(__name__)
api = Api(app)

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

''' Call back functions for new recordings and configuration requests
'''
api.add_resource(NewRecording, '/camera/api/v1.0/newrecording', endpoint = 'newrecording')
api.add_resource(reoconfig.ReoConfig, '/camera/api/v1.0/reoconfig', endpoint = 'reoconfig')

if __name__ == '__main__':
    registration_not_done = True
    while (registration_not_done):
        try:
            # Register callback REST API for configuration request for Reolink camera's
            r = requests.post("http://"+cia+":80/rest/camera_listeners/", 
                              json={
                                "url": "http://"+cia+":5102/camera/api/v1.0/reoconfig", 
                                "description": "Config callback for Reolink camera's", 
                                "callback_type": 'config'
                                }, 
                              timeout=10)
            if r.status_code == 201 or r.status_code == 400:
                registration_not_done = False
            log.info("registration config status code %s", r.status_code)
        except Exception as e:
            log.error("%s", e)
        time.sleep(5)
    registration_not_done = True
    while (registration_not_done):
        try:
            # Register callback REST API for configuration request for Reolink camera's
            r = requests.post("http://"+cia+":80/rest/camera_listeners/", 
                              json={
                                "url": "http://"+cia+":5102/camera/api/v1.0/newrecording", 
                                "description": "Recording callback for Reolink camera's", 
                                "callback_type": 'ftp'
                                }, 
                              timeout=10)
            if r.status_code == 201 or r.status_code == 400:
                registration_not_done = False
            log.info("registration config status code %s", r.status_code)
        except Exception as e:
            log.error("%s", e)
        time.sleep(5)    
    # Hand over control to Flask.  Flask will trigger the above REST API
    app.run(host="0.0.0.0", port=5102)
