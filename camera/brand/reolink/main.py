import os
import time
import sys
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from recording import NewRecording
import reoconfig

app = Flask(__name__)
api = Api(app)

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

# bind resource for REST API service
api.add_resource(NewRecording, '/camera/api/v1.0/newrecording', endpoint = 'newrecording')
api.add_resource(reoconfig.ReoConfig, '/camera/api/v1.0/reoconfig', endpoint = 'reoconfig')

if __name__ == '__main__':
    registration_not_done = True
    while (registration_not_done):
        try:
            r = requests.post("http://"+cia+":8000/rest/camera_listeners/", 
                              json={"url": "http://"+cia+":5102/camera/api/v1.0/reoconfig", "description": "", "callback_type": 'config'}, 
                              timeout=10)
            if r.status_code == 201 or r.status_code == 400:
                registration_not_done = False
            print(r.status_code)
        except Exception as e:
            print(e)
        time.sleep(5)
    registration_not_done = True
    while (registration_not_done):
        try:
            r = requests.post("http://"+cia+":5101/ftp/api/v1.0/registerclient",
                              json={"url": "http://"+cia+":5102/camera/api/v1.0/newrecording", "callback_type": 'config'},
                              timeout=10)
            if r.status_code == 201:
                registration_not_done = False
            print(r.status_code)
        except Exception as e:
            print(e)
        time.sleep(5)
    app.run(host="0.0.0.0", port=5102)
