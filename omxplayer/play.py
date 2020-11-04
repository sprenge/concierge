import os
import time
import sys
from multiprocessing import Process
import subprocess
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class VideoStream(Resource):
    '''
    REST API class for creation/deletion of video stream on a (part of the) screen of the raspberry.
    Create is done one by one
    Delete removes ALL video streams at once
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('url', type = str, required = True, location = 'json')
        self.reqparse.add_argument('x1', type = int, required = True, location = 'json')
        self.reqparse.add_argument('y1', type = int, required = True, location = 'json')
        self.reqparse.add_argument('x2', type = int, required = True, location = 'json')
        self.reqparse.add_argument('y2', type = int, required = True, location = 'json')
        self.reqparse.add_argument('sound', type = bool, required = False, default=False, location = 'json')
        self.reqparse.add_argument('hdmi', type = int, required = False, default=0, location = 'json')
        super(VideoStream, self).__init__()

    def post(self):
        '''
        Creates a video stream on a part of the screen
        '''
        args = self.reqparse.parse_args()
        p = Process(target=play_stream, args=(args['url'], args['x1'], args['y1'], args['x2'], args['y2'], args['sound'], args['hdmi']))
        p.start()
        return {}, 201

    def delete(self):
        '''
        Removes all video streams from all screens
        '''
        os.system('pkill -9 omxplayer')
        os.system('reset')
        return {}, 201

class ScreenProperties(Resource):
    '''
    REST API class to retrieve the screen characteristics
    '''
    def get(self):
        res = get_screen_resolution()
        return {"screen_resolution": res}, 200

# bind resource for REST API service
api.add_resource(VideoStream, '/stream/api/v1.0/tasks', endpoint = 'tasks')
api.add_resource(ScreenProperties, '/screen/api/v1.0/resolution', endpoint = 'resolution')

def get_screen_resolution():
    p = subprocess.Popen(['fbset', '-s'], stdout=subprocess.PIPE)
    for line in p.stdout:
        line = str(line)
        if '1920x1080' in line:
            return "HD"
    return ""

def play_stream(url, x1, y1, x2, y2, sound, hdmi):
    win = str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2) 
    cmd_list =  ['omxplayer', '--blank']
    if sound:
        cmd_list.append('-n')
        cmd_list.append('-1')
    cmd_list.append('--win')
    cmd_list.append(win)
    cmd_list.append(url)
    p = subprocess.Popen(['omxplayer', '-n', '-1', '--blank', '--win', win, url], stdout=subprocess.PIPE)
    p.communicate()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
