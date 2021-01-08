'''
Triggered when an asset is received as a result of camera motion :
The camera name (deduced from the filename) is returned when the camera is found is the camera
  database and is of type reolink and recording record is add into the database for mp4 files. 
'''
import os
import time
import sys
import logging
import re
import datetime
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

def parse_date_time(dt):
    match = re.match("(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d).*", dt)
    epoch_time = 0
    if match:
        epoch_time = datetime.datetime(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4)),
            int(match.group(5)),
            int(match.group(6)),
        ).timestamp()
    epoch_time = int(epoch_time) + time.timezone
    return int(epoch_time)

def is_reolink_asset(args_file):
    '''
    Is the asset produced by a reolink camera or not ?
    Returns :
    - reolink asset : True or False
    - camera dict
    - camera name
    - file extension
    '''
    head, tail = os.path.split(args_file)
    file_name_parts = tail.split("_")

    if len(file_name_parts) > 0:
        cam_name = file_name_parts[0]
        filename, file_extension = os.path.splitext(tail)
        file_extension = file_extension.replace('.', '')
        if file_extension in ['mp4', 'jpg']:
            try:
                url = "http://"+cia+":8000/rest/cameras/"
                r = requests.get(url)
                if r.status_code == 200:
                    for camera in r.json():
                        if camera['name'] == cam_name:
                            if camera['brand']['brand']['name'] == 'Reolink':
                                if file_extension == 'jpg':
                                    os.remove('/root'+args_file)  # not required
                                return True, camera, cam_name, file_extension
            except Exception as e:
                print(e)

    return False, None, '', ''

class NewRecording(Resource):
    '''
    REST API class for creation/deletion of video stream on a (part of the) screen of the raspberry.
    Create is done one by one
    Delete removes ALL video streams at once
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type = str, required = True, location = 'json')
        super(NewRecording, self).__init__()

    def post(self):
        '''
        Creates a video stream on a part of the screen
        '''
        args = self.reqparse.parse_args()
        head, tail = os.path.split(args['file'])
        file_name_parts = tail.split("_")
        ret_json = {}
        print("New recording", args)
        reolink_asset, camera, cam_name, file_extension = is_reolink_asset(args['file'])
        print(reolink_asset, camera, cam_name, file_extension)
        if reolink_asset:

            date_time = file_name_parts[2]
            ret_json = {
                'camera_name': cam_name, 
                'type': file_extension,
                'analytics_profile': camera['analytics_profile'],
                'epoch': parse_date_time(date_time)
            }
            if file_extension == 'mp4':
                # create a recording record
                dt = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(ret_json['epoch']-time.timezone))
                data = {"camera": camera['id']}
                data['file_path_video'] = args['file']
                data['recording_date_time'] = dt
                # data['file_path_snapshot'] = args['file'].replace(".mp4", '.jpg')
                pre, ext = os.path.splitext(args['file'])
                # data['url_thumbnail'] = "http://"+cia+":8000"+pre+'.gif'
                data['url_video'] = "http://"+cia+":8000"+pre+'.mp4'
                # data['url_snapshot'] = "http://"+cia+":8000"+pre+'.jpg'
                url = "http://"+cia+":8000/rest/recordings/"
                try:
                    r = requests.post(url, json=data, timeout=10)
                    if r.status_code != 201:
                        log.error("Create recording failed {}".format(r.status_code))
                    else:
                        ret_json['id'] = str(r.json()['id'])
                except Exception as e:
                    log.error(str(e))


        return ret_json, 201

if __name__ == '__main__':
    date_time = "20201201202416.jpg"
    print(parse_date_time(date_time))
