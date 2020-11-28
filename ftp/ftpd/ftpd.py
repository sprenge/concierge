import os
import re
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

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
print("sending ip address : ", cia)

class myFTPHandler(FTPHandler):
    def on_file_received(self, file):
        match = re.match("^/root(.*)", file)
        if match:
            file  = match.group(1)
        data = {"file": file}
        camera_name = ''
        snapshot_url = None
        file_type = ''
        for url in clients:
            print("url", url)
            try:
                r = requests.post(url, json=data, timeout=3)
                if r.status_code == 201:
                    ret_data = r.json()
                    if 'camera_name' in ret_data:
                        camera_name = ret_data['camera_name']
                    if 'type' in ret_data:
                        file_type = ret_data['type']
            except Exception as e:
                print(e)
        
        # Trigger the motion service based on the presence of a jpeg
        # TBC : Is this reolink specific ???
        if file_type == 'jpg':
            try:
                data = {'file': file, 'type': file_type, 'camera_name': camera_name}
                if snapshot_url:
                    data['snapshot_url'] = snapshot_url
                url = "http://"+cia+":5104/motion/api/v1.0/motion_detected"
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
