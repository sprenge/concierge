import cv2
import imutils
import face_recognition
import time


fn = "snap/cut119.jpg"

start_time = time.time()
image = cv2.imread(fn)
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

boxes = face_recognition.face_locations(rgb, model="hog")
print(boxes)
for top, right, bottom, left in boxes:
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

print(time.time()-start_time)
image = imutils.resize(image, width=800)
cv2.imwrite("snap.jpg", image)

