import os
import time
import sys
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from login import httpLogin
from configure import Osd, SystemGeneral, Ftp

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

print("cia_config", cia)

class ReoConfig(Resource):
    '''
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('brand', type = str, required = True, location = 'json')
        self.reqparse.add_argument('host', type = str, required = True, location = 'json')
        self.reqparse.add_argument('user', type = str, required = True, location = 'json')
        self.reqparse.add_argument('password', type = str, required = True, location = 'json')
        self.reqparse.add_argument('timezone', type = str, required = True, location = 'json')
        super(ReoConfig, self).__init__()

    def post(self):
        '''
        '''
        args = self.reqparse.parse_args()
        name = args['name']

        ret_payload = {}
        if args['brand'] == "Reolink":
            l = httpLogin(args['host'], args['user'], args['password'])
            token = l.get_token()
            print(token)
            if not token:
                return {}, 400
            print("Got valid token : Reconfigure Reolink camera ", name)
        
            ftp = Ftp(token, args['host'], cia)
            new_p = {'user': 'user', 'password': '12345'}
            ftp.put_data(new_p)
            payload = {}
            osd = Osd(token, args['host'])
            new_p = {"name": name}
            osd.put_data(new_p)
            sg = SystemGeneral(token, args['host'])
            new_p = {"timezone": -3600}
            sg.put_data(new_p)                            
            ret_payload['snapshot_url'] = 'http://'+args['host']+'/cgi-bin/api.cgi?cmd=Snap&amp;channel=0&amp;rs=wuuPhkmUCeI9WG7C&amp;user='+args['user']+'&amp;password='+args['password']
            ret_payload['live_url_hd'] = 'rtsp://'+args['user']+':'+args['password']+'@'+args['host']+':554//h264Preview_01_main'
            ret_payload['live_url_sd'] = 'rtsp://'+args['user']+':'+args['password']+'@'+args['host']+':554//h264Preview_01_sub'

        return ret_payload, 201

