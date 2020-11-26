import time
import numpy as np
import argparse
import cv2

pt = './pi-object-detection/MobileNetSSD_deploy.prototxt.txt'
ca = './pi-object-detection/MobileNetSSD_deploy.caffemodel'

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

testfile = "erwin1.mp4"
cf = 0.6

video_captured = cv2.VideoCapture(testfile)
print("testing", testfile)

fps = video_captured.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
frame_count = int(video_captured.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count/fps

print('fps = ' + str(fps))
print('number of frames = ' + str(frame_count))
print('duration (S) = ' + str(duration))
minutes = int(duration/60)
seconds = duration%60
print('duration (M:S) = ' + str(minutes) + ':' + str(seconds))

frame_nbr = 0
start_time = time.time()
while (video_captured.isOpened()):
    # read frame-by-frame
    ret, image = video_captured.read()
    if ret == False:
        break

    if frame_nbr < 150:
        frame_nbr+= 1
        continue
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
            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            if CLASSES[idx] == 'person':
                print("[INFO] {}".format(label))
                cv2.rectangle(image, (startX, startY), (endX, endY), COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                cv2.imwrite("/home/administrator/snap/frame%d.jpg" % frame_nbr, image)
    frame_nbr += 1
