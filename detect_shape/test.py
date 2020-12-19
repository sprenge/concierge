import sys
from main import find_shape
import cv2

fn = sys.argv[0]
cap = cv2.VideoCapture(fn)
ret = 1
frame_nbr = 0
while ret:
    ret, frame = cap.read()
    alist = find_shape(frame, frame_nbr)
    print(frame_nbr, alist)
    frame += 1
