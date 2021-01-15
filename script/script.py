# In settings.json first activate computer vision mode: 
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

# execution: python script.py [path] [number of images]
# example usage: python script.py C:/tensorflow/models/research/object_detection/images/ 200
# creates a "train" ,"test" and "val" folder at the given path containing the given number of images in total and a cocodata.json for each folder
# the total number of images could differ from the given number because pictures without any plants aren't saved

import setup_path 
import airsim
import cocoformat as coco

import tempfile
import os
import time
import numpy as np
import shutil
import cv2
from os import path
import random
import sys

imagepath = sys.argv[1]

if os.path.exists(imagepath):
    shutil.rmtree(imagepath, ignore_errors = True)

totalnum = int(sys.argv[2])
testnum = int(totalnum / 10) # 10%
valnum = testnum # 10%
trainnum = totalnum - (2*testnum) # 80%
numbers = [testnum, valnum, trainnum]

# connect to the AirSim simulator 
client = airsim.VehicleClient()
client.confirmConnection()

emptyidx = -1
numidx = -1
prevemptyidx = emptyidx
skypictures = 0

def save_pictures(responses, imagepath, name, idx, emptyidx):

    for response in responses:
        filename = imagepath + name + str(idx) 
        
        #the following 4 lines are copied from PythonClient/car/hello_car.py
        if not os.path.exists(imagepath):
            os.makedirs(imagepath)
       
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
        img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 3 channel image array H X W X 3

        if name == "segmentation":
            #if the picture has no plants (sky picture), don't save it and it's annotations
            if coco.calculateannotations(img_rgb,response.width,response.height, idx):
                return idx                            
        else:
            if idx != emptyidx:
                coco.appendimage(idx, response.width, response.height, name + str(idx) + '.png')     
                cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # write to png 
        idx += 1
    return emptyidx

for num in numbers:
    numidx +=1
    if numidx == 0:
        folder = "test/"
    elif numidx == 1:
        folder = "val/"
    else:
        folder = "train/"

    for x in range(num): # do few times
        print(folder +"scene"+ str(x) + "...", end = " ", flush = True)

        #use a smaller area for camera placement to prevent taking pictures of the sky
        xcoord = random.random()* 20 - 10 #[-10,10]
        ycoord = random.random()* 20 - 10 #[-10,10]
        zcoord = random.random() * -0.1 #[-0.1,0]

        #these numbers are the result of try and error
        pitch = random.random() * 0.5 - 1.7 #[-1.2,-1.7] #random.random() * 3 - 2 #[-2 1]
        roll = random.random() * 0.5  #[0,1]
        yaw = random.random() * 100 #[0,100]
    
        client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(xcoord, ycoord, zcoord), airsim.to_quaternion(pitch, roll, yaw)), True)
    
        #take segementation picture
        responses = client.simGetImages([airsim.ImageRequest("1", airsim.ImageType.Segmentation, False, False),])
        emptyidx = save_pictures(responses,imagepath + folder,"segmentation", x, emptyidx)
        
        #emptyidx changes everytime a picture was empty and hasn't been saved. 
        #this is used to count the number of not-saved images
        if emptyidx != prevemptyidx:
            skypictures += 1
        
        prevemptyidx = emptyidx

        #take regular picture
        responses = client.simGetImages([airsim.ImageRequest("1", airsim.ImageType.Scene, False, False),])
        save_pictures(responses, imagepath + folder, "scene", x, emptyidx)

        print(" ...done!")

    coco.createjson(imagepath + folder)
    coco.reset()
# currently reset() doesn't work in CV mode. Below is the workaround
print(str(skypictures) + " pictures deleted.")
client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0)), True)
