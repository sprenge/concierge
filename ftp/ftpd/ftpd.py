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
from PIL import Image

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

def make_thumbnail(p):
    '''
    Create thumbnail for still image"
    '''
    basewidth = 200
    try:
        img = Image.open(p)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        pre, ext = os.path.splitext(p)
        img.save(pre + '.gif')
    except Exception as e:
        log.error(e)

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

def get_registered_clients():
    clients = []
    try:
        r = requests.get("http://"+cia+":8000/rest/camera_listeners/", timeout=5)
        if r.status_code == 200:
            for rec in r.json():
                if rec['callback_type'] == 'ftp':
                    print('found ftp client', rec['url'])
                    clients.append(rec['url'])
        else:
            log.error("camera_listeners error {}".format(r.status_code))
    except Exception as e:
        log.error(str(e))
    return clients

class myFTPHandler(FTPHandler):
    def on_file_received(self, file):
        # file received from camera via ftp
        match = re.match("^/root(.*)", file)
        if match:
            file  = match.group(1)
        data = {"file": file}
        camera_name = ''
        file_type = ''
        epoch = ''
        analytics_profile = ''
        recording_id = ''
        clients = get_registered_clients()
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
                    if 'analytics_profile' in ret_data:
                        analytics_profile = ret_data['analytics_profile']
                        if not analytics_profile:
                            analytics_profile = ""
                    if 'id' in ret_data:
                        recording_id= ret_data['id']              
            except Exception as e:
                log.error("%s", e)
        
        # Trigger the motion service based on the presence of a jpeg
        # which means that type field is filled in with jgp
        if file_type == 'jpg':
            # make_thumbnail('/root'+file)
            try:
                data = {
                    'file': file, 
                    'type': file_type, 
                    'camera_name': camera_name,
                    'analytics_profile': analytics_profile,
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
                    'analytics_profile': analytics_profile,
                    'id': recording_id,
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

server = FTPServer(("0.0.0.0", 21), handler)
server.max_cons = 256
server.max_cons_per_ip = 5
server.serve_forever()
