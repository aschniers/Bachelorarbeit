import pprint
import tempfile
import os
import time
import numpy as np
import json
import copy
from pycocotools import mask
from skimage import measure

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
        "iscrowd" : 0,
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


def plantmask(img_rgb, plantcolour):
    """uses the segmentation image and the plantcolour to create a binary mask 
       and calculates the area (the amount of pixels) of the plant 
       and creates array objpos that contains the position of the object pixels

       Parameters:
       img_rgb: rgb array of the picture
       plantcolour: rgb value of the plant

       Returns:
       list: counts
       int: area
       list: objpos
    """
    area = 0
    objpos = [] #positions of the object pixels (is used to calculate the bbox)
    segmentation = []
    #create empty array in the same size as the picture
    mask = [[None] * len(img_rgb) for i in range(len(img_rgb[0]))]

    #compare the rgb triplets with the object
    for ij in np.ndindex(img_rgb.shape[:2]):
        #print()
        if np.all(img_rgb[ij] != plantcolour): #if the pixel doens't belong to the plant
            mask[ij[0]][ij[1]] = 0
        else:
            mask[ij[0]][ij[1]] = 1
            area += 1
            objpos.append(ij)

    #print array for testing purposes        
    for i in range(len(mask)):
        print()
        for j in range(len(mask[i])):
           print(mask[i][j], end = " ")
    print()
    print()

    mask = np.array(mask)

    #https://github.com/cocodataset/cocoapi/issues/131
    contours = measure.find_contours(mask, 0.5, fully_connected = 'high')
    for contour in contours:
        contour = np.flip(contour, axis=1)
        segmentation = contour.ravel().tolist()

    if segmentation:
        print(segmentation)
    return mask, area, objpos

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
    [oatcounts, oatarea, oatpos] = plantmask(img_rgb, oatcolour)
    [wheatcounts, wheatarea, wheatpos] = plantmask(img_rgb, wheatcolour)
    
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
    
