import os
import math
import logging
import time
import threading
import json
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import cv2
import numpy as np
import face_recognition
from PIL import Image
from yolo import find_shape

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

position_tracker = set()

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

def make_pixel_key(x, y):
    return str(x)+'_'+str(y)

def get_pixel_pos(key):
    l = key.split("_")
    return int(l[0]), int(l[1])

def is_close_pixel(new_key):
    '''
    Is the new_key (=string) close to another position ? :
    - True : yes
    - False : not found, added in position tracker
    '''
    global position_tracker
    max_distance = 50

    x1, y1 = get_pixel_pos(new_key)
    fnd = None
    for akey in position_tracker:
        x2, y2 = get_pixel_pos(akey)
        dist2 = (y2-y1)**2 + (x2-x1)**2
        dist = int(math.sqrt(dist2))
        if dist < max_distance:
            fnd = akey

    if fnd:
        return True
    position_tracker.add(new_key) # add to the pixel database
    return False

def filter_unique_positions(fsl):
    '''
    Remove duplicated on same center position
    '''
    global position_tracker

    new_list = []
    for rec in fsl:
        # calculate center position
        startX = int(rec['box']['startX'])
        startY = int(rec['box']['startY'])
        endX = int(rec['box']['endX'])
        endY = int(rec['box']['endY'])
        x_pos = startX + int((endX-startX)/2)
        y_pos = startY + int((endY-startY)/2)
        pixel_key = make_pixel_key(x_pos, y_pos)
        if not is_close_pixel(pixel_key):
            new_list.append(rec)

    return new_list

class FindShape(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        self.reqparse.add_argument('type', type = str, required = False, location = 'json')
        self.reqparse.add_argument('file_base', type = str, required = False, location = 'json', store_missing='')
        self.reqparse.add_argument('recording_id', type = str, required = False, location = 'json', store_missing='')
        self.reqparse.add_argument('desired_shapes', type = str, required = False, location = 'json', store_missing='')
        self.reqparse.add_argument('confidence_level', type = float, required = False, location = 'json', store_missing=0.7)
        self.reqparse.add_argument('analyse_each_n_frames', type = int, required = False, location = 'json', store_missing=5)
        super(FindShape, self).__init__()

    def post(self):
        '''
        Receive request to find shapes in an image file or video file
        Supports two file formats (file suffixes) : jpg and mp4
        '''
        global position_tracker
        args = self.reqparse.parse_args()
        st = time.time()
        shape_list = []
        recording_id = None
        file_base = None
        desired_shapes = args['desired_shapes']
        confidence_level = args['confidence_level']
        analyse_each_n_frames = args['analyse_each_n_frames']
        desired_shapes_list = json.loads(desired_shapes)
        try:
            recording_id = args['recording_id']
            file_base = args['file_base']
        except:
            pass

        position_tracker = set()
        log.debug("start_find_shape for {}".format(args['file']))
        print(args)
        cap = cv2.VideoCapture(args['file'])

        if args['type'] == 'mp4':
            ret = 1
            frame_nbr = 0
            while ret:
                ret, frame = cap.read()
                if ret:
                    if frame_nbr % analyse_each_n_frames == 0:
                        fsl = find_shape(
                            frame, 
                            frame_nbr=frame_nbr, 
                            recording_id=recording_id, 
                            file_base=file_base, 
                            desired_shapes=desired_shapes_list, 
                            confidence_level=confidence_level,
                            cia=cia)
                        up_list = filter_unique_positions(fsl)
                        shape_list.extend(up_list)
                    if frame_nbr == 30:
                        try:
                            # write first jpg to disk
                            fn = args['file'].replace(".mp4", ".jpg")
                            cv2.imwrite(fn, frame)
                            make_thumbnail(fn)
                            fn_base = fn.replace('/root', '')
                            fn_t = args['file'].replace(".mp4", ".gif")
                            fn_t_base = fn_t.replace('/root', '')
                            r = requests.get("http://"+cia+":8000/rest/recordings/"+str(recording_id))
                            if r.status_code == 200:
                                rec_data = r.json()
                                rec_data['file_path_snapshot'] = fn.replace('/root', '')
                                rec_data['url_snapshot'] = "http://"+cia+":8000"+fn_base
                                rec_data['url_thumbnail'] = "http://"+cia+":8000"+fn_t_base
                                headers = {"Content-Type": "application/json"}
                                r = requests.put("http://"+cia+":8000/rest/recordings/"+str(recording_id)+'/', data=json.dumps(rec_data), headers=headers)
                        except Exception as e:
                            print(e)
                    frame_nbr += 1
        log.debug("end_find_shape for {}".format(args['file']))
        log.debug("find shape processing time %s", time.time()-st)
        if shape_list:
            log.debug("find shape shape_list %s", shape_list)
        return shape_list, 201

class GetVideoClipMetaData(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        super(GetVideoClipMetaData, self).__init__()

    def post(self):
        '''
        Get following data from the mp4 video clip
        '''
        args = self.reqparse.parse_args()
        data = {}

        video_captured = cv2.VideoCapture(args['file'])
        
        fps = video_captured.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(video_captured.get(cv2.CAP_PROP_FRAME_COUNT))
        try:
            duration = frame_count/fps

            data['fps'] = fps
            data['frame_count'] = frame_count
        except Exception as e:
            log.error("{}".format(args['file']))
            log.error(str(e))

        return data, 201


# bind resource for REST API service
api.add_resource(FindShape, '/shape/api/v1.0/find_shape', endpoint = 'find_shape')
api.add_resource(GetVideoClipMetaData, '/shape/api/v1.0/get_video_metadata', endpoint = 'get_video_metadata')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
log.info("CONCIERGE_IP_ADDRESS %s", cia)

try:
    lport = int(os.environ['PORT_DETECT_SHAPE'])
except:
    lport = 5103

app.run(host="0.0.0.0", port=lport)
