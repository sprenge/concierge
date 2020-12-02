import os
import re
import logging
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

clients = [] # list of endpoint to trigger
app = Flask(__name__)
api = Api(app)

class NewClient(Resource):
    '''
    REST API class for creation/deletion of video stream on a (part of the) screen of the raspberry.
    Create is done one by one
    Delete removes ALL video streams at once
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('url', type = str, required = True, location = 'json')
        super(NewClient, self).__init__()

    def post(self):
        '''
        Creates a video stream on a part of the screen
        '''
        args = self.reqparse.parse_args()
        clients.append(args['url'])
        print(clients)
        return {}, 201

# bind resource for REST API service
api.add_resource(NewClient, '/ftp/api/v1.0/registerclient', endpoint = 'registerclient')


def register_clients():
    app.run(host="0.0.0.0", port=5101)

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
log.info("cia %s", cia)

class myFTPHandler(FTPHandler):
    def on_file_received(self, file):
        match = re.match("^/root(.*)", file)
        if match:
            file  = match.group(1)
        data = {"file": file}
        camera_name = ''
        file_type = ''
        epoch = ''
        for url in clients:
            log.debug("send post request to ftp hook %s", url)
            try:
                r = requests.post(url, json=data, timeout=3)
                if r.status_code == 201:
                    ret_data = r.json()
                    if 'camera_name' in ret_data:
                        # camera is recognized by the ftp hook
                        camera_name = ret_data['camera_name']
                    if 'type' in ret_data:
                        file_type = ret_data['type']
                    if 'epoch' in ret_data:
                        epoch = ret_data['epoch']
            except Exception as e:
                log.error("%s", e)
        
        # Trigger the motion service based on the presence of a jpeg
        # which means that type field is filled in with jgp
        if file_type == 'jpg':
            try:
                data = {
                    'file': file, 
                    'type': file_type, 
                    'camera_name': camera_name,
                    'epoch' : epoch
                }
                url = "http://"+cia+":5104/motion/api/v1.0/motion_detected"
                r = requests.post(url, json=data, timeout=5)
            except:
                pass

        # Trigger the motion service with the message that the recording is ready
        # and has been received
        if file_type == 'mp4':
            try:
                data = {
                    'file': file, 
                    'type': file_type, 
                    'camera_name': camera_name,
                    'epoch': epoch
                }
                url = "http://"+cia+":5104/motion/api/v1.0/recording_ready"
                r = requests.post(url, json=data, timeout=5)
            except:
                pass

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/root/static/recordings", perm="elradfmwMT")
#authorizer.add_anonymous("/home/nobody")

# handler = FTPHandler
handler = myFTPHandler
handler.authorizer = authorizer
handler.passive_ports = range(30000, 30009)

register_client_t = threading.Thread(target=register_clients, args=())
register_client_t.start()
server = FTPServer(("0.0.0.0", 21), handler)
server.max_cons = 256
server.max_cons_per_ip = 5
server.serve_forever()
