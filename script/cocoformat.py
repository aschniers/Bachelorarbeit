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

data['info'].append({"description": "coco dataset from pictures taken in Unreal"})
data['categories'].append({
    "supercategory" : "plant",
    "id" : 1,
    "name" : "wheat"})
data['categories'].append({
    "supercategory" : "plant",
    "id" : 2,
    "name" : "oats"})

def appendimage(image_id, width, height, filename):
    data['images'].append({
        "id": image_id,
        "height" : height,
        "width" : width,
        "file_name" : filename})

def appendannotation(annotation_id, category_id, size, counts, area, image_id, bbox):
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
    
    with open(path + 'cocodata.json', 'w') as outfile:
        json.dump(data,outfile, indent = 4)


def plantcounts(img_rgb, plantcolour):
    #uses the segmentation image and the plantcolour to create a counts array 
    #calculates the area/ amount of pixels of the object
    pixcnt = 0
    objcnt = 0
    area = 0
    counts = []
    objpos = [] #position of the object pixels
    #counts has to start with not-object pixels
    #if the first pixel is the object, counts starts with 0
    if np.all(img_rgb[0][0] == plantcolour):
        counts.append(pixcnt)
    #compare the rgb triplets with the object colours and create the counts array
    for ij in np.ndindex(img_rgb.shape[:2]):
        if np.all(img_rgb[ij] != plantcolour):
            pixcnt += 1
            if objcnt != 0:
                counts.append(objcnt)
            objcnt = 0
        else:
            objpos.append(ij)
            objcnt += 1
            if pixcnt != 0:
                counts.append(pixcnt)
            area += objcnt
            pixcnt = 0
    #add the last entry
    if objcnt != 0:
        counts.append(objcnt)
    if pixcnt != 0:
        counts.append(pixcnt)  

    return counts, area, objpos


def calculatebbox(objpos, width):
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
    global annotation_id
    blue = [152, 253, 245] #oats, yellow on the picture
    violet = [184, 81, 185] #wheat
    [oatcounts, oatarea, oatpos] = plantcounts(img_rgb, blue)
    [wheatcounts, wheatarea, wheatpos] = plantcounts(img_rgb, violet)
    
    if oatarea:
        oatbbox = calculatebbox(oatpos, width)
        annotation_id +=1
        appendannotation(annotation_id-1, 1,[width,height],oatcounts,oatarea,image_id,oatbbox)
    
    if wheatarea:
        wheatbbox = calculatebbox(wheatpos, width)
        annotation_id +=1
        appendannotation(annotation_id-1, 2,[width,height],wheatcounts,wheatarea,image_id,wheatbbox)
        
    if not oatarea + wheatarea:
        return True
    else:
       return False

def reset():
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
 
