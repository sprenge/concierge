import os
import cv2

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]

pt = './pi-object-detection/MobileNetSSD_deploy.prototxt.txt'
ca = './pi-object-detection/MobileNetSSD_deploy.caffemodel'

def find_shape(image, frame_nbr=0, recording_id=None, file_base=None, desired_shapes=[], confidence_level=0.7), cia='127.0.0.1':
    shape_list = []
    net = cv2.dnn.readNetFromCaffe(pt, ca)

    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    net.setInput(blob)
    detections = net.forward()

    item_nbr = 0
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > confidence_level:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            try:
                idx = int(detections[0, 0, i, 1])
                shape = CLASSES[idx]
                if shape in desired_shapes:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    adict = {'shape': shape, 'confidence': confidence * 100}
                    pos = {"startX": int(startX), "startY": int(startY), "endX": int(endX), "endY": int(endY)}
                    adict["box"] = pos
                    adict["frame_nbr"] = frame_nbr
                    obj_str = "_snapshot{}_{}{}_frame{}".format(str(recording_id), adict['shape'], item_nbr, str(frame_nbr))
                    if recording_id and file_base:
                        fn = file_base+obj_str+".jpg"
                        crop_img = image[startY:endY, startX:endX]
                        cv2.imwrite(fn, crop_img)
                        adict['snapshot'] = fn
                        url = 'http://'+cia+':8000'+fn.replace('/root', '')
                        adict['snapshot_url'] = url
                    shape_list.append(adict)
                    item_nbr += 1
            except Exception as e:
                print(str(e))
    return shape_list