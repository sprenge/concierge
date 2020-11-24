import os
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
        data = {"file": file}
        for url in clients:
            print("trigger :", url)
            try:
                r = requests.post(url, json=data, timeout=10)
            except:
                pass

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/root", perm="elradfmwMT")
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
