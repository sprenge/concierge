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
        self.reqparse.add_argument('ip_address', type = str, required = True, location = 'json')
        self.reqparse.add_argument('user', type = str, required = True, location = 'json')
        self.reqparse.add_argument('password', type = str, required = True, location = 'json')
        self.reqparse.add_argument('timezone', type = str, required = True, location = 'json')
        super(ReoConfig, self).__init__()

    def post(self):
        '''
        '''
        args = self.reqparse.parse_args()
        name = args['name']

        if args['brand'] == "Reolink":
            l = httpLogin(args['ip_address'], args['user'], args['password'])
            token = l.get_token()
            print(token)
            if not token:
                return {}, 400
            print("Got valid token : Reconfigure Reolink camera ", name)
        
            ftp = Ftp(token, args['ip_address'], cia)
            new_p = {'user': 'user', 'password': '12345'}
            ftp.put_data(new_p)
            payload = {}
            osd = Osd(token, args['ip_address'])
            new_p = {"name": name}
            osd.put_data(new_p)
            sg = SystemGeneral(token, args['ip_address'])
            new_p = {"timezone": -3600}
            sg.put_data(new_p)                            
        


        return {}, 201

