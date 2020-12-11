import os
import logging
import time
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import cv2
import numpy as np
import face_recognition

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

pt = './pi-object-detection/MobileNetSSD_deploy.prototxt.txt'
ca = './pi-object-detection/MobileNetSSD_deploy.caffemodel'

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]

app = Flask(__name__)
api = Api(app)
cf = 0.6

def find_shape(image, frame_nbr=0):
    shape_list = []
    net = cv2.dnn.readNetFromCaffe(pt, ca)

    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    net.setInput(blob)
    detections = net.forward()

    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > cf:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            adict = {'shape': CLASSES[idx], 'confidence': confidence * 100}
            pos = {"startX": int(startX), "startY": int(startY), "endX": int(endX), "endY": int(endY)}
            adict["box"] = pos
            adict["frame_nbr"] = frame_nbr
            adict['faces'] = []
            if CLASSES[idx] == 'person':
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model="hog")
                for top, right, bottom, left in boxes:
                    face = {"top": int(top), 'right': int(right), 'bottom': int(bottom), 'left': int(left)}
                    adict['faces'].append(face)
            shape_list.append(adict)
    return shape_list

class FindShape(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        self.reqparse.add_argument('type', type = str, required = False, location = 'json')
        super(FindShape, self).__init__()

    def post(self):
        '''
        Receive request to find shapes in an image file or video file
        Supports two file formats (file suffixes) : jpg and mp4
        '''
        args = self.reqparse.parse_args()
        st = time.time()
        shape_list = []

        cap = cv2.VideoCapture(args['file'])
        if args['type'] == "jpg":
            ret, frame = cap.read()
            shape_list = find_shape(frame, frame_nbr=0)

        if args['type'] == 'mp4':
            ret = 1
            frame_nbr = 0
            skip_f = 5
            skip_c = skip_f
            while ret:
                ret, frame = cap.read()
                if ret:
                    if skip_c == 0:
                        fsl = find_shape(frame, frame_nbr)
                        shape_list.extend(fsl)
                        skip_c = skip_f
                    else:
                        skip_c = skip_c - 1
                    frame_nbr += 1

        log.debug("find shape processing %s", time.time()-st)
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
        print("get video data for ", args['file'])
        
        fps = video_captured.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(video_captured.get(cv2.CAP_PROP_FRAME_COUNT))
        try:
            duration = frame_count/fps

            data['fps'] = fps
            data['frame_count'] = frame_count
            print("video metadata", data)
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
