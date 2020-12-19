import cv2
import numpy as np
import face_recognition
import pickle

fn = "erwin.jpg"
cap = cv2.VideoCapture(fn)
ret, frame = cap.read()


rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
boxes = face_recognition.face_locations(rgb, model="hog")
# compute the facial embedding for the face
encodings = face_recognition.face_encodings(rgb, boxes)
# print(len(encodings), type(encodings))
fr = open("test.data", "wb")
fr.write(pickle.dumps(encodings))
fr.close()

print("start comparing")
fn = "erwin2.jpg"
cap = cv2.VideoCapture(fn)
ret, frame = cap.read()


rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
boxes = face_recognition.face_locations(rgb, model="hog")
# compute the facial embedding for the face
encodings2 = face_recognition.face_encodings(rgb, boxes)

for encoding in encodings:
    print(encoding)
    matches = face_recognition.compare_faces([encodings], encoding)
    print(matches)
