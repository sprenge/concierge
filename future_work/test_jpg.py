import os
import time
from PIL import Image

files = ["/camera/2020/11/23/CameraLisa_01_20201123120756.jpg", "/camera/2020/11/23/CameraLisa_01_20201123120757.jpg"]

for filename in files:
    start = time.time()
    try:
        im = Image.open(filename)
        im.verify() #I perform also verify, don't know if he sees other types o defects
        im.close() #reload is necessary in my case
        im = Image.open(filename)
        im.transpose(Image.FLIP_LEFT_RIGHT)
        im.close()
        im=Image.open(filename)
        print(im)
        # do stuff
    except Exception as e:
        print(e)
    print (time.time()-start)

