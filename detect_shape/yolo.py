import numpy as np
import time
import cv2


LABELS_FILE='./yolo/coco.names'
# CONFIG_FILE='./yolo/yolov3.cfg'
CONFIG_FILE='./yolo/yolov4-tiny.cfg'
# WEIGHTS_FILE='./yolo/yolov3.weights'
WEIGHTS_FILE='./yolo/yolov4-tiny.weights'
CONFIDENCE_THRESHOLD = 0.3

LABELS = open(LABELS_FILE).read().strip().split("\n")
# net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHTS_FILE)
# print("net_yolo", net)

def find_shape(image, frame_nbr=0, recording_id=None, file_base=None, desired_shapes=[], confidence_level=0.7, cia='127.0.0.1'):
    shape_list = []

    (H, W) = image.shape[:2]
    net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHTS_FILE)
    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > CONFIDENCE_THRESHOLD:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, CONFIDENCE_THRESHOLD)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        item_nbr = 0
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            try:
                shape = LABELS[classIDs[i]]
                if shape in desired_shapes:
                    print("shape_found", confidences[i], confidence_level)
                    if confidences[i] > confidence_level:
                        adict = {'shape': shape, 'confidence': confidences[i] * 100}
                        pos = {"startX": x, "startY": y, "endX": x+w, "endY": y+h}
                        adict["box"] = pos
                        adict["frame_nbr"] = frame_nbr
                        obj_str = "_snapshot{}_{}{}_frame{}".format(str(recording_id), adict['shape'], item_nbr, str(frame_nbr))
                        if recording_id and file_base:
                            fn = file_base+obj_str+".jpg"
                            crop_img = image[y:y+h, x:x+w]
                            cv2.imwrite(fn, crop_img)
                            adict['snapshot'] = fn
                            url = 'http://'+cia+':8000'+fn.replace('/root', '')
                            adict['snapshot_url'] = url
                        shape_list.append(adict)
                        item_nbr += 1
            except Exception as e:
                print(str(e))
    return shape_list
