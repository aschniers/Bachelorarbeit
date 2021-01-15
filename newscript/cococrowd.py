import pprint
import tempfile
import os
import time
import numpy as np
import json


data = {}
data['info'] = []
data['images'] = []
data['annotations'] = []
data['categories'] = []
annotation_id = 0

#add information and category to the data dictionary:
data['info'].append({"description": "coco dataset from pictures taken in Unreal"})
data['categories'].append({
    "supercategory" : "plant",
    "id" : 1,
    "name" : "wheat"})
data['categories'].append({
    "supercategory" : "plant",
    "id" : 2,
    "name" : "oat"})

def appendimage(image_id, width, height, filename):
    """
    add information about the image to the data dictionary

    Parameters:
    image_id: image id
    width: width of the picture
    height: height of the picture
    filename: name of the picture, without the path: "scene" + image_id
    """
    data['images'].append({
        "id": image_id,
        "height" : height,
        "width" : width,
        "file_name" : filename})

def appendannotation(annotation_id, category_id, size, counts, area, image_id, bbox):
    """
    add the annotation to the data dictionary in json format

    Parameters:
    annotation_id: id of the annotation
    category_id: id of the category
    size: width and height of the picture
    counts: counts array, that was created in plantcounts()
    area: amount of plant_pixels
    image_id: image id
    bbox: bounding box of the plant(s)
    """
    data['annotations'].append({
        "id": annotation_id,
        "category_id" : category_id,
        "iscrowd" : 1,
        "segmentation" : {
            "size": size,
            "counts" : counts
            },
        "image_id": image_id,
        "area" : area,
        "bbox" : bbox})


def createjson(path):
    """
    create json file and write the cocodata to it

    Parameters:
    path: path to save the file to
    """
    with open(path + 'cocodata.json', 'w') as outfile:
        json.dump(data,outfile, indent = 4)


def plantcounts(img_rgb, plantcolour):
    """uses the segmentation image and the plantcolour to create a counts array 
       and calculates the area (the amount of pixels) of the plant

       Parameters:
       img_rgb: rgb array of the picture
       plantcolour: rgb value of the plant

       Returns:
       list: counts
       int: area
       list: objpos
    """
    
    pixcnt = 0
    objcnt = 0
    area = 0
    counts = []
    objpos = [] #positions of the object pixels
    #counts has to start with not-object pixels
    #if the first pixel is the object, counts starts with 0
    if np.all(img_rgb[0][0] == plantcolour):
        counts.append(pixcnt)
    #compare the rgb triplets with the object colours and create the counts array
    for ij in np.ndindex(img_rgb.shape[:2]):
        
        ##################################################################################
        #I used this part to find the rgb values of the plants.
        #if a new unreal project is created the segementation picture has different colours

        #boden = True
        #himmel = True
        
        #if np.all(img_rgb[ij] != [205, 143, 222]):
        #    boden = False
        #if np.all(img_rgb[ij] != [130, 219, 128]):
        #    himmel = False
        #if (himmel == False and boden ==False):
        #    print("test: "+str(img_rgb[ij[0]][ij[1]]))
        #else:
        #    print("else: "+str(img_rgb[ij[0]][ij[1]]))
        ##################################################################################

        if np.all(img_rgb[ij] != plantcolour): #if the pixel doens't belong to the plant
            pixcnt += 1 #increase the number of not-plant pixels in a row
            if objcnt != 0: #if a row of plant-pixels has been interrupted, add the number of plant pixels in a row to the counts array
                counts.append(objcnt)
            objcnt = 0 #set plant-pixels in a row to 0
        else:
            objpos.append(ij) #if the pixel belongs to the plant, add the postion of that pixel to objpos
            objcnt += 1
            if pixcnt != 0:
                counts.append(pixcnt)
            area += objcnt
            pixcnt = 0
    #add the last entry:
    if objcnt != 0:
        counts.append(objcnt)
    if pixcnt != 0:
        counts.append(pixcnt)  

    return counts, area, objpos


def calculatebbox(objpos, width):
    """
    calculates the boundingbox of the plant

    Parameters:
    objpos: list, that contains all the positions of the plant-pixels in order (row by row, top to bottom)
    width: width of the picture

    Returns:
    bbox: list, boundingbox of the plant
    """
    bbox = [width,0,0,0] 
    #bbox[x-coordinate for top left pixel, y-coordinate for top left pixel, bbox width, bbox height]
    bbox[1]=objpos[0][0]
    bbox[3]=objpos[len(objpos)-1][0] - bbox[1] +1
    maxwidth = 0
    for i in range(len(objpos)) :
        if objpos[i][1] < bbox[0]:
            bbox[0] = objpos[i][1]
        if objpos[i][1] > maxwidth:
            maxwidth = objpos[i][1]

    bbox[2] = maxwidth - bbox[0] + 1

    return bbox


def calculateannotations(img_rgb, width, height, image_id):
    """
    calls all necessary functions to get the information to save as annotation

    Parameters:
    img_rgb: rgb array of the picture
    width: width of the pictures
    height: height of the picture
    image_id: id of the picture that the annotations are created for

    Returns
    boolean, ture if the picture is empty
    """
    global annotation_id
    oatcolour = [228, 193, 244] #colour of the oats in the segmentation picture 
    wheatcolour = [207, 91, 108] #colour of the wheat in the segementation picture
    [oatcounts, oatarea, oatpos] = plantcounts(img_rgb, oatcolour)
    [wheatcounts, wheatarea, wheatpos] = plantcounts(img_rgb, wheatcolour)
    
    if oatarea:
        oatbbox = calculatebbox(oatpos, width)
        annotation_id +=1
        appendannotation(annotation_id-1, 1,[width,height],oatcounts,oatarea,image_id,oatbbox)
    
    if wheatarea:
        wheatbbox = calculatebbox(wheatpos, width)
        annotation_id +=1
        appendannotation(annotation_id-1, 2,[width,height],wheatcounts,wheatarea,image_id,wheatbbox)
    
    #if there are no plants on the picture, return true
    if not oatarea + wheatarea:
        return True
    else:
       return False

def reset():
    """
    empty the dictionary "data" and prepare it to start a new cocodata file
    """
    global annotation_id
    data.clear()
    data['info'] = []
    data['images'] = []
    data['annotations'] = []
    data['categories'] = []
    data['info'].append({"description": "coco dataset from pictures taken in Unreal"})
    data['categories'].append({
        "supercategory" : "plant",
        "id" : 1,
        "name" : "wheat"})
    data['categories'].append({
        "supercategory" : "plant",
        "id" : 2,
        "name" : "oats"})
    annotation_id = 0
    
