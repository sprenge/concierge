import os
import re
import logging
import time
import copy
import threading
import datetime
from shutil import copyfile
import requests
from flask import Flask, jsonify, redirect, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import influxdb

lock = threading.Lock()
flush_out_after = 90 # Flush object into the database older than this value
image_list_len = 10 # maximum number of images per shape_type
state_db = []  # keep track of recent events
image_db = {}  # dictionary with key shape_type, data is a list of images (oldest last)

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
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def time2epoch(s):
    match = re.match("^(\d{4})-(\d{2})-(\d{2})-(\d{2}):(\d{2}).*", s)
    appendix_time_influx = '000000000'
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        local_time = int(datetime.datetime(year,month,day,hour,minute).timestamp())
        print("local_time", local_time, time.timezone)
        time_utc = local_time - time.timezone
        epoch = str(time_utc)
        epoch = epoch + appendix_time_influx
        return epoch
    return "0"

def age_db():
    while(1):
        time.sleep(5)
        lock.acquire()
        for record in reversed(state_db):
            if int(time.time()) > record['timestamp']+flush_out_after:
                print("remove record from state_db", record)
                state_db.remove(record)
        lock.release()

def get_shape_ojects():
    url = "http://"+cia+":8000/rest/analytics_shapes/"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            alist = r.json()
            alist.append({"shape": "all", "id": 99})
            return alist
        else:
            log.error("GetShapeObjects status code {}".format(r.status_code))
    except Exception as e:
        log.error(str(e))

        return []

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
            r = requests.get("http://"+cia+":8000/rest/recordings/"+str(recording_id))
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


class GetVideoShapes(Resource):
    '''
    REST API class getting shapes for a given period
    '''
    def __init__(self):
        super(GetVideoShapes, self).__init__()

    def get(self, shape, start_time, end_time):
        '''
        get list of shapes in a specific timeframe (start_time, end_time)
        '''
        appendix_time_influx = '000000000'

        start_time_influx = str(start_time)+appendix_time_influx
        end_time_influx = str(end_time)+appendix_time_influx
        start_time_influx = time2epoch(start_time)
        end_time_influx = time2epoch(end_time)
        client = influxdb.InfluxDBClient(host=cia, port=8086)
        client.switch_database('concierge')
        query = "select * from camera_shapes_detected_video where \"time\">={} and \"time\"<={}".format(start_time_influx, end_time_influx)

        results = client.query(query)
        parsed_list = list(results.get_points(measurement='camera_shapes_detected_video'))
        shape_list = []
        for rec in parsed_list:
            if shape == 'all':
                shape_list.append(rec)
            else:
                if rec['shape'] == shape:
                    shape_list.append(rec)
        return shape_list, 200, {'Access-Control-Allow-Origin': '*'}

class GetShapeObjects(Resource):
    '''
    REST API class getting shapes for a given recording
    '''
    def __init__(self):
        super(GetShapeObjects, self).__init__()

    def get(self):
        # shape_objects = []
        # shape_objects.append({"id": "all", "name": "all"})
        # shape_objects.append({"id": "person", "name": "person"})
        shape_list = get_shape_ojects()

        return shape_list, 200, {'Access-Control-Allow-Origin': '*'}

class CreateKnownObject(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('recording_id', type = str, required = True, location = 'json')
        self.reqparse.add_argument('frame_nbr', type = str, required = True, location = 'json')
        self.reqparse.add_argument('snapshot', type = str, required = True, location = 'json')
        self.reqparse.add_argument('shape', type = str, required = True, location = 'json')
        super(CreateKnownObject, self).__init__()

    def post(self):
        '''
        Create a known object into the database
        '''
        args = self.reqparse.parse_args()
        src_fn = args['snapshot']
        dummy_path, fn = os.path.split(src_fn)
        if os.path.exists(src_fn):
            copyfile(src_fn, "/root/static/ko/"+fn)
            url = "http://"+cia+":8000/rest/known_objects/"
            data = {}
            data['recording_id'] = args['recording_id']
            data['frame_nbr'] = args['frame_nbr']
            data['file_path_image'] = "/root/static/ko/"+fn
            if len(args['name']) == 0:
                data['identified'] = False
            else:
                data['name'] = args['name']
            shape_list = get_shape_ojects()
            fnd_shape = None
            for rec in shape_list:
                if rec['shape'] == args['shape']:
                    data['object_type'] = rec['id']
            print("data", data)
            try:
                r = requests.post(url, json=data)
                print(r.status_code)
            except Exception as e:
                log.error(str(e))
        
        
        return {}, 201, {'Access-Control-Allow-Origin': '*'}

class RegisterDetectedShapes(Resource):
    '''
    Concierge detected shapes, keep track of detected objects for a while so that automation
    systems (like home assistant) can poll for state
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('shape_type', type = str, required = True, location = 'json')
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('snapshot_url', type = str, required = True, location = 'json')
        self.reqparse.add_argument('time', type = str, required = True, location = 'json')
        super(RegisterDetectedShapes, self).__init__()

    def post(self):
        '''
        Create a detected shape into the state database
        '''
        args = self.reqparse.parse_args()
        t = args['time']
        record = {'type': 'shape'}
        shape_type = args['shape_type']
        record['shape_type'] = shape_type
        record['camera_name'] = args['camera_name']
        record['snapshot_url'] = args['snapshot_url']
        record['time'] = t
        record['timestamp'] = int(time.time())
        lock.acquire()
        if shape_type not in image_db:
            image_db[shape_type] = []
        image_db[shape_type].insert(0,args['snapshot_url'])
        if len(image_db[shape_type]) > image_list_len:
            del image_db[shape_type][-1]
        state_db.append(record)        
        lock.release()

        return {}, 201, {'Access-Control-Allow-Origin': '*'}

class ShapesDetected(Resource):
    '''
    REST API class getting shapes for a given recording
    '''
    def __init__(self):
        super(ShapesDetected, self).__init__()

    def get(self, camera_name, shape_type):
        shape_dict = {"detected": False}
        if camera_name== "all_cameras":
            lock.acquire()
            copy_db = copy.deepcopy(state_db)
            lock.release()
            for record in copy_db:
                if record['shape_type'] == shape_type:
                    if record['type'] == 'shape':
                        shape_dict['detected'] = True
                        shape_dict['camera_name'] = record['camera_name']
                        shape_dict['shape_type'] = shape_type
                        shape_dict['snapshot_url'] = record['snapshot_url']
        else:
            # specific camera
            pass

        return shape_dict, 200, {'Access-Control-Allow-Origin': '*'}

class LastDetectedImages(Resource):
    '''
    REST API return last image detected
    '''
    def __init__(self):
        super(LastDetectedImages, self).__init__()

    def get(self, shape_type, sequence_nbr):
        # all_types
        seq_nbr = int(sequence_nbr)
        if seq_nbr >= image_list_len:
            seq_nbr = image_list_len - 1
        print(image_db, shape_type, seq_nbr)
        if shape_type != 'all_shapes':
            try:
                url = image_db[shape_type][seq_nbr]
                print(url)
                redirect(url)
            except Exception as e:
                print(str(e))

        return [], 200, {'Access-Control-Allow-Origin': '*'}


@app.route('/interworking/api/v1.0/last_detected_images/<shape_type>/<sequence_nbr>.jpg', methods=['GET'])
def last_detected_images(shape_type, sequence_nbr):
    seq_nbr = int(sequence_nbr)
    if seq_nbr >= image_list_len:
        seq_nbr = image_list_len - 1
    if shape_type != 'all_shapes':
        url = image_db[shape_type][seq_nbr]
        r = requests.get(url)
        if r.status_code == 200:
            data = None
            for chunk in r.iter_content(1024):
                if data:
                    data += chunk
                else:
                    data = chunk
            response = make_response(data)
            response.headers.set('Content-Type', 'image/jpeg')
            response.headers.set('Content-Disposition', 'attachment', filename='%s.jpg' % seq_nbr)
            return response



# bind resource for REST API service
api.add_resource(ShapesVideoInflux, '/interworking/api/v1.0/shapes_video/<string:recording_id>', endpoint = 'shapes_video')
api.add_resource(GetRecordings, '/interworking/api/v1.0/get_recordings/<string:shape>/<int:start_time>/<int:end_time>', endpoint = 'get_recordings')
api.add_resource(GetVideoShapes, '/interworking/api/v1.0/get_video_shapes/<string:shape>/<string:start_time>/<string:end_time>', endpoint = 'get_video_shapes')
api.add_resource(GetShapeObjects, '/interworking/api/v1.0/get_shape_objects', endpoint = 'get_shape_objects')
api.add_resource(CreateKnownObject, '/interworking/api/v1.0/create_known_object', endpoint = 'create_known_object')
api.add_resource(RegisterDetectedShapes, '/interworking/api/v1.0/register_detected_shape', endpoint = 'register_detected_shape')
api.add_resource(ShapesDetected, '/interworking/api/v1.0/shape_detected/<string:camera_name>/<string:shape_type>', endpoint = 'shape_detected')
# api.add_resource(LastDetectedImages, '/interworking/api/v1.0/last_detected_images/<string:shape_type>/<string:sequence_nbr>', endpoint = 'last_detected_images')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

log.info("CONCIERGE_IP_ADDRESS %s", cia)

t1 = threading.Thread(target=age_db, args=())
t1.start()
app.run(host="0.0.0.0", port=5107)
