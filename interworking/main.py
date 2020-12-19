import os
import logging
import time
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import influxdb

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

class ShapesVideoInflux(Resource):
    '''
    REST API class getting shapes for a given recording
    '''
    def __init__(self):
        # self.reqparse = reqparse.RequestParser()
        # self.reqparse.add_argument('recording_id', type = str, required = True, location = 'json')
        super(ShapesVideoInflux, self).__init__()

    def get(self, recording_id):
        '''
        Receive request to find shapes in an image file or video file
        Supports two file formats (file suffixes) : jpg and mp4
        '''
        # args = self.reqparse.parse_args()

        client = influxdb.InfluxDBClient(host=cia, port=8086)
        client.switch_database('concierge')
        query = "select * FROM camera_shapes_detected_video WHERE \"recording_id\"='{}'".format(recording_id)
        results = client.query(query)
        try:
            columns = results.raw['series'][0]['columns']
        except:
            return [], 200
        object_link_template = None
        try:
            r = requests.get("http://"+cia+":80/rest/recordings/"+str(recording_id))
            if r.status_code == 200:
                object_link_template = r.json()['url_video']
        except Exception as e:
            log.error("get recording error {}".format(str(e)))
        index2name = {}
        for i, name in enumerate(columns):
            index2name[i] = name
        recording_shape_list = []
        for rec in results.raw['series'][0]['values']:
            adict = {}
            for i, aval in enumerate(rec):
                adict[index2name[i]] = aval
            if object_link_template:
                object_link = object_link_template.replace('.mp4', "_object_"+str(recording_id)+"_"+str(adict['frame_nbr'])+".jpg")
                adict['object_link'] = object_link
            recording_shape_list.append(adict)

        return recording_shape_list, 200

class GetRecordings(Resource):
    '''
    REST API class getting shapes for a given recording
    '''
    def __init__(self):
        super(GetRecordings, self).__init__()

    def get(self, shape, start_time, end_time):
        '''
        get list of recording ids based on the filter arguments 
        - shape : all or specific shape (person, car, ...)
        - start_time, end_time
        '''

        client = influxdb.InfluxDBClient(host=cia, port=8086)
        client.switch_database('concierge')
        query = "select recording_id from camera_shapes_detected_video where \"time\">={} and \"time\"<={}".format(start_time, end_time)

        if shape != "all":
            query = "select recording_id from camera_shapes_detected_video where \"time\">={} and \"time\"<={} and \"shape\"='{}'".format(start_time, end_time, shape)
        results = client.query(query)
        parsed_list = list(results.get_points(measurement='camera_shapes_detected_video'))
        recording_set = set()
        for rec in parsed_list:
            recording_set.add(rec['recording_id'])

        return list(recording_set), 200

        

# bind resource for REST API service
api.add_resource(ShapesVideoInflux, '/interworking/api/v1.0/shapes_video/<string:recording_id>', endpoint = 'shapes_video')
api.add_resource(GetRecordings, '/interworking/api/v1.0/get_recordings/<string:shape>/<int:start_time>/<int:end_time>', endpoint = 'get_recordings')

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '192.168.1.59'

log.info("CONCIERGE_IP_ADDRESS %s", cia)

app.run(host="0.0.0.0", port=5107)
