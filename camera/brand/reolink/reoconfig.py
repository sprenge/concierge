import os
import time
import sys
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

class ReoConfig(Resource):
    '''
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type = str, required = True, location = 'json')
        super(ReoConfig, self).__init__()

    def post(self):
        '''
        '''
        args = self.reqparse.parse_args()
        # print(args['file'])
        return {}, 201

