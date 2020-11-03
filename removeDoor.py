# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 21:22:53 2020

@author: Allan
"""

import urllib

try:
    from xml.etree import cElementTree as ET
except ImportError as e:
    from xml.etree import ElementTree as ET

import base64
import zlib
import numpy as np
import struct
#import requests
import matplotlib.pyplot as plt
import math

def getLonLat():
    return [40.726875, -73.957249]

def getPanoId(lonLat):
    url = "http://maps.google.com/cbk?output=xml&ll=" + str(lonLat[0]) + "," + str(lonLat[1]) + "&dm=1"
    xml = urllib.request.urlopen(url)
    tree = ET.parse(xml)
    root = tree.getroot()
    pano = {}
    for child in root:
        if child.tag == 'data_properties':
            pano[child.tag] = child.attrib
    return pano['data_properties']['pano_id']

def downloadxml(output_file, pano_id):
    url = "http://maps.google.com/cbk?output=xml&cb_client=maps_sv&hl=en&dm=1&pm=1&ph=1&renderer=cubic,spherical&v=4&panoid="
    xml = urllib.request.urlopen(url + pano_id)
    with open(output_file + ".xml", 'wb') as f:
        for line in xml:
            f.write(line)

def getDepthMap(path_to_metadata_xml):
    pano_xml = open(path_to_metadata_xml, 'rb')
    tree = ET.parse(pano_xml)
    root = tree.getroot()
    for child in root:
        if child.tag == 'model':
            root = child[0]
    return root.text;
    
def getWidthHeight(path_to_metadata_xml):
    pano = {}
    pano_xml = open(path_to_metadata_xml, 'rb')
    tree = ET.parse(pano_xml)
    root = tree.getroot()
    for child in root:
        if child.tag == 'data_properties':
            pano[child.tag] = child.attrib
    return (int(pano['data_properties']['image_width']),int(pano['data_properties']['image_height']))

def parse(b64_string):
    # fix the 'inccorrect padding' error. The length of the string needs to be divisible by 4.
    b64_string += "=" * ((4 - len(b64_string) % 4) % 4)
    # convert the URL safe format to regular format.
    data = b64_string.replace("-", "+").replace("_", "/")

    data = base64.b64decode(data)  # decode the string
    data = zlib.decompress(data)  # decompress the data
    return np.array([d for d in data])

def parseHeader(depthMap):
    return {
        "headerSize": depthMap[0],
        "numberOfPlanes": getUInt16(depthMap, 1),
        "width": getUInt16(depthMap, 3),
        "height": getUInt16(depthMap, 5),
        "offset": getUInt16(depthMap, 7),
    }

def get_bin(a):
    ba = bin(a)[2:]
    return "0" * (8 - len(ba)) + ba

def getUInt16(arr, ind):
    a = arr[ind]
    b = arr[ind + 1]
    return int(get_bin(b) + get_bin(a), 2)

def getFloat32(arr, ind):
    return bin_to_float("".join(get_bin(i) for i in arr[ind : ind + 4][::-1]))

def bin_to_float(binary):
    return struct.unpack("!f", struct.pack("!I", int(binary, 2)))[0]

def parsePlanes(header, depthMap):
    indices = []
    planes = []
    n = [0, 0, 0]

    for i in range(header["width"] * header["height"]):
        indices.append(depthMap[header["offset"] + i])

    for i in range(header["numberOfPlanes"]):
        byteOffset = header["offset"] + header["width"] * header["height"] + i * 4 * 4
        n = [0, 0, 0]
        n[0] = getFloat32(depthMap, byteOffset)
        n[1] = getFloat32(depthMap, byteOffset + 4)
        n[2] = getFloat32(depthMap, byteOffset + 8)
        d = getFloat32(depthMap, byteOffset + 12)
        planes.append({"n": n, "d": d})

    return {"planes": planes, "indices": indices}

def pcData(x, y, pointCloud):
    return str(x) + " " + str(y) + ": " + str(pointCloud[3*(y * 512 + x)]) + " " + str(pointCloud[3*(y * 512 + x) + 1]) + " " + str(pointCloud[3*(y * 512 + x) + 2])

def findLatLon(path_to_metadata_xml):
    pano = {}
    pano_xml = open(path_to_metadata_xml, 'rb')
    tree = ET.parse(pano_xml)
    root = tree.getroot()
    for child in root:
        if child.tag == 'projection_properties':
            pano[child.tag] = child.attrib
        if child.tag == 'data_properties':
            pano[child.tag] = child.attrib
    
    return (float(pano['data_properties']['lat']), float(pano['data_properties']['lng']), float(pano['projection_properties']['pano_yaw_deg']))

def deg2rad(degrees):
    return math.pi*degrees/180.0

def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))

def latBSearch(treeLL, target):
    l = 0
    r = len(treeLL) - 1
    while l < r:
        m = (int) ((l+r) / 2)
        if treeLL[m][0] < target:
            l = m + 1
        else:
            r = m - 1
    return l

def findTreesInBox(treeLL, latRange, minL, maxL):
    result = []
    for i in range(latRange[0], latRange[1] + 1):
        if treeLL[i][1] >= minL and treeLL[i][1] <= maxL:
            result.append((treeLL[i][0], treeLL[i][1]))
    return result
    
def drawImage():
    data = plt.imread(output_file + ".jpeg")
    fig, ax = plt.subplots(figsize=(32, 16), dpi=96)
    ax.imshow(data, interpolation='none')
    plt.axis('off')  
    plt.show()
    saveImagePath = "C:/Allan/Streetview/dataCollection/" + pano_id + ".jpeg"
    plt.savefig(saveImagePath, bbox_inches='tight', pad_inches=0)

def removeDoors(planes, box, label, isRight):
    for ar in box:
        ar[0] = ar[0] * 3584 / 1000
        ar[2] = ar[2] * 3584 / 1000
        ar[1] = ar[1] * 2560 / 1000
        ar[3] = ar[3] * 2560 / 1000
    for ar in box:
        ar[0] = int(ar[0] / 32) + 64
        ar[2] = int(ar[2] / 32) + 64
        if isRight:
            ar[0] += 272
            ar[2] += 272
        ar[1] = int(ar[1] / 32) + 96
        ar[3] = int(ar[3] / 32) + 96
    i = 0
    while i < len(box):
        if label[i] == 1:
            ar = box[i]
            tl = ar[1] * 512 + ar[0]
            tr = ar[1] * 512 + ar[2]
            bl = ar[3] * 512 + ar[0]
            br = ar[3] * 512 + ar[2]
            if planes[tl] != planes[tr]:
                print("ERROR")
            if planes[tl] != planes[bl] or planes[tr] != planes[br]:
                i+=1
                continue
            remove = True
            for j in range(len(box)):
                if label[j] == 3:
                    stair = box[j]
                    if not (stair[0] > ar[2] + 3 or stair[2] + 3 < ar[0] or stair[1] > ar[3] + 5 or stair[3] + 5 < ar[1]):
                        bls = (stair[3] + 5) * 512 + stair[0]
                        brs = (stair[3] + 5) * 512 + stair[2]
                        if planes[tl] != planes[bls] or planes[tr] != planes[brs]:
                            remove = False
            if remove:
                box.pop(i)
                label.pop(i)
                i-=1
        i+=1
    

lonLat = getLonLat()
pano_id = getPanoId([lonLat[0], lonLat[1]])
output_file = "C:/Allan/Streetview/xml/" + pano_id
downloadxml(output_file, pano_id)

depthMap = getDepthMap(output_file + ".xml")
depthMapData = parse(depthMap)
header = parseHeader(depthMapData)
data = parsePlanes(header, depthMapData)
planes = data["indices"]

boxes = [[452.50149536, 313.84585571, 549.86987305, 568.07366943],
 [936.59753418, 209.52201843, 999.21472168, 448.19122314],
 [811.59173584, 224.12611389, 888.20977783, 442.44238281],
 [244.02230835, 163.73001099, 361.4442749, 465.77758789],
 [603.55706787, 201.21325684, 765.51367188, 527.63140869],
 [383.58148193, 655.39440918, 461.89001465, 951.38824463],
 [454.67077637, 416.02297974, 481.59820557, 470.01239014],
 [455.12573242, 551.19152832, 572.01867676, 663.01269531],
 [600.6192627,  523.77740479, 772.13739014, 624.06738281],
 [787.97125244, 503.22055054, 983.56835938, 588.80474854]]

label = [1, 1, 1, 1, 1, 1, 2, 3, 3, 3]

removeDoors(planes, boxes, label, True)

print(boxes)
print(label)