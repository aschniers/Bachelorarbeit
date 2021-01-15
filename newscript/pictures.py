# execution: python script.py [path] [number of images]

# example usage: python script.py C:/tensorflow/models/research/object_detection/images/ 200
# creates a "train" ,"test" and "val" folder at the given path containing the given number of images in total and a cocodata.json for each folder
# the total number of images could differ from the given number because pictures without any plants aren't saved

#python pictures.py c:/Users/user/Documents/pictures/ 20

import setup_path 
import airsim
### choose 'cococrowd' if a crowd of plants is depicted or 'cocosingle' if a single plant is depicted
import cocosingle as coco

import tempfile
import os
import time
import numpy as np
import shutil
import cv2
from os import path
import random
import sys
from timeit import default_timer as timer

timestart = timer()


def save_pictures(responses, imagepath, name, idx, emptyidx):
    """
    save image as png

    Parameters:
    responses: pictures that have been taken
    imagepath: path that the images are saved to
    name: identifies if the picture is a regular or a segmentation picture, is either "scene" or "segmentation"
    idx: index of the picture
    emptyidx: index of an empty picture

    Returns:
    int: emptyidx

    """

    for response in responses:
        filename = imagepath + name + str(idx) #name of the saved picture
        
        #the following 4 lines are copied from PythonClient/car/hello_car.py
        if not os.path.exists(imagepath): #create new folger if it doesn't exist
            os.makedirs(imagepath)
       
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
        img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 3 channel image array H X W X 3

        #the annotations are made using the segmentation pictures, not the scene pictures
        if name == "segmentation":
            #if the picture has no plants (sky picture), don't save it and it's annotations
            #print(img_rgb)
            if coco.calculateannotations(img_rgb,response.width,response.height, idx):
                return idx    
        #save the picture only if it's a scene picture, don't save segmentation pictures
        else:
            if idx != emptyidx: #if the picture is not empty
                coco.appendimage(idx, response.width, response.height, name + str(idx) + '.png') #add picture to cocodata   
                cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # save picture as png

        idx += 1
    return emptyidx

def take_pictures(xcoords, ycoord,zcoord, numbers):
    """
    place camera in the scene and take pictures
    
    Parameters:
    xcoords: list of xcoords, read from positions.txt
    ycoord: ycoord, read from positions.txt
    zcoord: zcoord, read from positions.txt
    numbers: list of numbers of test, val and train pictures

    """

    i = 0 #temp index of the xcoords
    idx = 0 #index of the xcoords
    factor = 1 #toggles between 1 and -1 to switch between landscape places
    numidx = -1 #index of numbers
    emptyidx = -1 #index of pictures without plants on it
    prevemptyidx = emptyidx
    skypictures = 0 # number of pictures without plants

    for num in numbers:
        numidx +=1
        if numidx == 0:
            folder = "test/"#"val/"
        elif numidx == 1:
            folder = "val/"
        else:
            folder = "train/"
        for x in range(num): # do few times
            print(folder +"scene"+ str(x) + "...", end = " ", flush = True)

            factor = -factor #used to toggle between landscape sides and camera angles
            xcoord = xcoords[idx] #current xcoord
            i += 0.5 
            idx = int(i) #use the same xcoord twice before stepping forward to the next
            if idx > len(xcoords)-1 : #if the last xcoord is reached, start from the beginning
                idx = 0
            
            pitch = -1.5 #- 0.5 + random.random() #-1.5 -> camera points to the ground
            roll = 0 
            yaw = 0

            client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(xcoord, (ycoord + (random.random()*2) -1) * factor, zcoord), airsim.to_quaternion(pitch, roll, yaw * factor)), True) #place camera using the coords and angles
            #client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(xcoord, ycoord , zcoord), airsim.to_quaternion(pitch, roll, yaw)), True) #place camera using the coords and angles
    
            #take segementation picture:
            responses = client.simGetImages([airsim.ImageRequest("1", airsim.ImageType.Segmentation, False, False),])
            emptyidx = save_pictures(responses,imagepath + folder,"segmentation", x, emptyidx)
        
            #emptyidx changes everytime a picture was empty and hasn't been saved. 
            #this is used to count the number of not-saved images
            if emptyidx != prevemptyidx:
                skypictures += 1
        
            prevemptyidx = emptyidx

            #take regular picture:
            responses = client.simGetImages([airsim.ImageRequest("1", airsim.ImageType.Scene, False, False),])
            save_pictures(responses, imagepath + folder, "scene", x, emptyidx)

            print(" ...done!")

        coco.createjson(imagepath + folder)
        coco.reset()




imagepath = sys.argv[1]

#create folder at given path
if os.path.exists(imagepath):
    shutil.rmtree(imagepath, ignore_errors = True)

totalnum = int(sys.argv[2]) #total number of pictures that should be taken
testnum = int(totalnum / 10) # 10% 
valnum = testnum # 10%
trainnum = totalnum - (2*testnum) # 80%
numbers = [testnum, valnum, trainnum] #contains the numbers of test, val and train pictures

# connect to the AirSim simulator 
client = airsim.VehicleClient()
client.confirmConnection()

#emptyidx = -1 #index of pictures without plants on it
#prevemptyidx = emptyidx #temp index of empty pictues
skypictures = 0 # number of empty pictures

datei = open('C:/Users/annas/Documents/Python Scripts/positions.txt','r') #read file to find out the cordinates of the plants
lines = datei.read().split("\n")
firstline = lines[0].split(" ")
lines.pop(0)
lines.pop(-1)
ycoord = float(firstline[0])
#zcoord = float(firstline[1]) -0.5 #the ground in unreal is at z = 0 and in Airsim it's at z = 1
zcoord = random.random()/2 #max 0.5m above the ground
#convert list of strings to list of floats
xcoords = [float(i) for i in lines] #convert all the xcoords to floats

#client.simEnableWeather(True)
#client.simSetWeatherParameter(airsim.WeatherParameter.Dust, 0.9) #add rain or dust

take_pictures(xcoords, ycoord, zcoord, numbers)
print(str(skypictures) + " pictures deleted.") #print how many pictures were empty and have been deleted


# currently reset() doesn't work in CV mode. Below is the workaround

client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0)), True)

timeend = timer()
duration = timeend - timestart
print("time "+ str(duration.round(1)) + " s, average " + str((duration/ totalnum).round(1)) + " s")
