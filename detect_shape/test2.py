import numpy as np
import time
import cv2


LABELS_FILE='/root//darknet/data/coco.names'
CONFIG_FILE='/root/darknet/cfg/yolov3.cfg'
CONFIG_FILE='/root/darknet/cfg/yolov2-tiny.cfg'
CONFIG_FILE='/root/concierge/detect_shape/yolo/yolov4-tiny.cfg'
WEIGHTS_FILE='/root/yolov3.weights'
WEIGHTS_FILE='/root/yolov2-tiny.weights'
WEIGHTS_FILE='/root/concierge/detect_shape/yolo/yolov4-tiny.weights'
VF='test8.mp4'
CONFIDENCE_THRESHOLD=0.3

LABELS = open(LABELS_FILE).read().strip().split("\n")

np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHTS_FILE)
cap = cv2.VideoCapture(VF)

ret = True
frame_nbr = 0

global_start = time.time()

while ret:
    ret, image = cap.read()
    frame_nbr += 1
    # print("frame_nbr", frame_nbr)
    if not frame_nbr % 5 == 0:
        continue
   
    if ret:

        (H, W) = image.shape[:2]

        # determine only the *output* layer names that we need from YOLO
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]


        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        start = time.time()
        layerOutputs = net.forward(ln)
        end = time.time()

        # print("[INFO] YOLO took {:.6f} seconds".format(end - start))

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
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
        
                color = [int(c) for c in COLORS[classIDs[i]]]

                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                print("detected", LABELS[classIDs[i]], confidences[i], frame_nbr)
                text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # show the output image
                fn = "/root/tmp/e{}.jpg".format(frame_nbr)
                cv2.imwrite(fn, image)

    # if frame_nbr > 200:
    #     ret = False

global_end = time.time()
print("[INFO] YOLO took {:.6f} seconds".format(global_end - global_start))
