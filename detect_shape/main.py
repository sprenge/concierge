import os
import threading
import requests
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import cv2
import numpy as np

pt = './pi-object-detection/MobileNetSSD_deploy.prototxt.txt'
ca = './pi-object-detection/MobileNetSSD_deploy.caffemodel'

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]

app = Flask(__name__)
api = Api(app)
cf = 0.6

def find_shape(image):
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
            print("detected shape", CLASSES[idx], confidence * 100)
            print("position", startX, startY, endX, endY)

class FindShape(Resource):
    '''
    REST API class for the reception of motion on a given camera
    '''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('camera_name', type = str, required = True, location = 'json')
        self.reqparse.add_argument('file', type = str, required = False, location = 'json')
        super(FindShape, self).__init__()

    def post(self):
        '''
        Receive request to find shapes in an image file or video file
        Supports two file formats (file suffixes) : jpg and mp4
        '''
        args = self.reqparse.parse_args()
        # quick motion check on single image of the motion clip
        cap = cv2.VideoCapture(args['file'])
        ret, frame = cap.read()
        find_shape(frame)
        return {}, 201

# bind resource for REST API service
api.add_resource(FindShape, '/shape/api/v1.0/find_shape', endpoint = 'find_shape')


try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'

app.run(host="0.0.0.0", port=5103)
