# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 13:49:36 2020

@author: Jerry
"""

import urllib
import os
import io
from PIL import Image

try:
    from xml.etree import cElementTree as ET
except ImportError as e:
    from xml.etree import ElementTree as ET

import base64
import zlib
import numpy as np
import struct
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from geopy.geocoders import Nominatim

pano_id = "GlGveTEw-VSmN3mv_DVuKQ"
output_file = "C:/Allan/Streetview/panoramas/" + pano_id

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

def downloadPano():
    url = "http://maps.google.com/cbk?output=xml&cb_client=maps_sv&hl=en&dm=1&pm=1&ph=1&renderer=cubic,spherical&v=4&panoid="
    xml = urllib.request.urlopen(url + pano_id)
    with open(output_file + ".xml", 'wb') as f:
        for line in xml:
            f.write(line)
    wh = getWidthHeight(output_file + ".xml")
    #image_width = 16384
    image_width = wh[0]
    #image_height = 8192
    image_height = wh[1]
    im_dimension = (image_width, image_height)
    blank_image = Image.new('RGB', im_dimension, (0, 0, 0, 0))
    
    base_url = 'http://maps.google.com/cbk?'
    
    for y in range(int(round(image_height / 512.0))):
        for x in range(int(round(image_width / 512.0))):
            url_param = 'output=tile&zoom=' + str(5) + '&x=' + str(x) + '&y=' + str(
                y) + '&cb_client=maps_sv&fover=2&onerr=3&renderer=spherical&v=4&panoid=' + pano_id
            url = base_url + url_param

            # Open an image, resize it to 512x512, and paste it into a canvas
            req = urllib.request.urlopen(url)
            file = io.BytesIO(req.read())

            im = Image.open(file)
            im = im.resize((512, 512))

            blank_image.paste(im, (512 * x, 512 * y))
            print(x * 512, y * 512)
    
    print("ran")
    blank_image.save(output_file + '.jpeg')
    #change to 664
    os.chmod(output_file + '.jpeg', 664)
    
#downloadPano()   
depthMap = getDepthMap(output_file + ".xml")

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


def computeDepthMap(header, indices, planes):

    v = [0, 0, 0]
    w = header["width"]
    h = header["height"]

    depthMap = np.empty(w * h)
    pointCloud = np.empty(w * h * 3)

    sin_theta = np.empty(h)
    cos_theta = np.empty(h)
    sin_phi = np.empty(w)
    cos_phi = np.empty(w)

    for y in range(h):
        theta = (h - y - 0.5) / h * np.pi
        sin_theta[y] = np.sin(theta)
        cos_theta[y] = np.cos(theta)

    for x in range(w):
        phi = (w - x - 0.5) / w * 2 * np.pi + np.pi / 2
        sin_phi[x] = np.sin(phi)
        cos_phi[x] = np.cos(phi)

    for y in range(h):
        for x in range(w):
            planeIdx = indices[y * w + x]

            v[0] = sin_theta[y] * cos_phi[x]
            v[1] = sin_theta[y] * sin_phi[x]
            v[2] = cos_theta[y]

            if planeIdx > 0:
                plane = planes[planeIdx]
                t = np.abs(
                    plane["d"]
                    / (
                        v[0] * plane["n"][0]
                        + v[1] * plane["n"][1]
                        + v[2] * plane["n"][2]
                    )
                )
                #depthMap[y * w + (w - x - 1)] = t
                depthMap[y*w + (w-x-1)] = t
                pointCloud[3 * y * w + 3 * x] = v[0] * t 
                pointCloud[3 * y * w + 3 * x + 1] = v[1] * t
                pointCloud[3 * y * w + 3 * x + 2] = v[2] * t
            else:
                #depthMap[y * w + (w - x - 1)] = 9999999999999999999.0
                depthMap[y*w + (w-x-1)] = 9999999999999999999.0
                pointCloud[3 * y * w + 3 * x] = 9999999999999999999.0
                pointCloud[3 * y * w + 3 * x + 1] = 9999999999999999999.0
                pointCloud[3 * y * w + 3 * x + 2] = 9999999999999999999.0
    return {"width": w, "height": h, "depthMap": depthMap, "pointCloud": pointCloud}

# decode string + decompress zip
depthMapData = parse(depthMap)
# parse first bytes to describe data
header = parseHeader(depthMapData)
# parse bytes into planes of float values
data = parsePlanes(header, depthMapData)

def writePointCloud(pointCloud):
    with open(output_file + "pointCLoud.txt", 'w') as f:
        for x in range(512):
            for y in range(256):
                if(pointCloud[(y*512+x)] != 1e+19):
                    f.write(str(x) + " " + str(y) + ": " + str(pointCloud[3*(y * 512 + x)]) + " " + str(pointCloud[3*(y * 512 + x) + 1]) + " " + str(pointCloud[3*(y * 512 + x) + 2]) + " ")

def pcData(x, y, pointCloud):
    return str(x) + " " + str(y) + ": " + str(pointCloud[3*(y * 512 + x)]) + " " + str(pointCloud[3*(y * 512 + x) + 1]) + " " + str(pointCloud[3*(y * 512 + x) + 2])

# compute position and values of pixels
depthMap = computeDepthMap(header, data["indices"], data["planes"])
pointCloud = depthMap["pointCloud"]

'''
im = depthMap["depthMap"]
im[np.where(im == max(im))[0]] = 255
if min(im) < 0:
    im[np.where(im < 0)[0]] = 0
im = im.reshape((depthMap["height"], depthMap["width"])).astype(int)
# display image
plt.imshow(im)
plt.show()
'''

def findLatLon(path_to_metadata_xml):
    pano = {}
    pano_xml = open(path_to_metadata_xml, 'rb')
    tree = ET.parse(pano_xml)
    root = tree.getroot()
    for child in root:
        if child.tag == 'data_properties':
            pano[child.tag] = child.attrib
        if child.tag == 'projection_properties':
            pano[child.tag] = child.attrib
    
    return (float(pano['data_properties']['lat']),float(pano['data_properties']['lng']), float(pano['projection_properties']['pano_yaw_deg']))
    
latlon = findLatLon(output_file + ".xml")
clat = latlon[0]
clon = latlon[1]
yaw = latlon[2]
#print("camera:", str(clat) + ",", clon)

if(yaw > 180):
    yaw = yaw - 180
else:
    yaw = 180 + yaw

def latLonMap(pointCloud):
    latLon = np.empty(512*256*2)
    for x in range(512):
        for y in range(256):
            dx = pointCloud[(512*y + x) * 3]
            dy = pointCloud[(512*y + x) * 3 + 1]      
            if(dx == 9999999999999999999.0 or dy == 9999999999999999999.0):
                continue
            rdx = dx*np.cos(np.radians(yaw)) + dy*np.sin(np.radians(yaw))
            rdy = -1*dx*np.sin(np.radians(yaw)) + dy*np.cos(np.radians(yaw))
            dlat = rdy / 111111;
            dlon = rdx / (111111 * np.cos(np.radians(clat)));
            latLon[2*(y*512 + x)] = dlat + clat
            latLon[2*(y*512 + x) + 1] = dlon + clon
    return latLon

latLonMap = latLonMap(pointCloud)

def getLatLon(x, y):
    return [latLonMap[2*(y*512 + x)], latLonMap[2*(y*512 + x) + 1]]
    
def findImageCoord(lat, lon, yaw, clat, clon, pointCloud):
    dy = 111111 * (lat - clat);
    dx = 111111 * np.cos(np.radians(clat)) * (lon - clon);
    
    dangle = np.degrees(np.arctan(dy/dx))
    #check if dx and dy is 0??
    if dx < 0 and dy > 0:
        dangle += 180
    elif dx < 0 and dy < 0:
        dangle += 180
    elif dx > 0 and dy < 0:
        dangle += 360

    if dangle < 90:
        dangle = 90 - dangle
    else:
        dangle = 450 - dangle

    offset = dangle - yaw
    if offset < 0:
        offset += 360
    
   
    
    x = (int)((offset / 360) * 512)
    
    dist = np.sqrt(dx**2+dy**2)
    minD = dist
    miny = -1
    inPict = False
    for y in range(256):
        if(pointCloud[(512*y + x) * 3] != 9999999999999999999.0):
            rdx = pointCloud[(512*y + x) * 3]*np.cos(np.radians(yaw)) + pointCloud[(512*y + x) * 3 + 1]*np.sin(np.radians(yaw))
            rdy = -1*pointCloud[(512*y + x) * 3]*np.sin(np.radians(yaw)) + pointCloud[(512*y + x) * 3 + 1]*np.cos(np.radians(yaw))
            currD = np.sqrt(rdx**2+rdy**2)
            if(currD > dist):
                inPict = True
            if(np.abs(dist - currD) < minD):
                minD = np.abs(dist - currD)
                miny = y
    if not inPict:
        return[9999999999999999999.0, 9999999999999999999.0]
    return [x, miny]
print(latlon)
print(getLatLon(0, 154))
'''
printLonLat(500, 200)
print(findImageCoord(40.72627853534421, -73.98938900492712, yaw, clat, clon, pointCloud))
coords = findImageCoord(40.726144, -73.98965, yaw, clat, clon, pointCloud)
if coords[0] == 9999999999999999999.0:
    print("Not in picture")
else:
    print(coords[0], coords[1])
    printLonLat(coords[0], coords[1])
'''
#chose pixel on image, red click blue predict  
'''   
data = plt.imread(output_file + ".jpeg")

fig, ax = plt.subplots()

ax.imshow(data, interpolation='none')

plt.show()

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
    xCoord = int(event.xdata)
    yCoord = int(event.ydata)
    square = patches.Rectangle((xCoord,yCoord), 50,50, color='RED')
    ax.add_patch(square)
    lonLat = getLonLat(int(xCoord / 32), int(yCoord / 32))
    pCoords = findImageCoord(lonLat[0], lonLat[1], yaw, clat, clon, pointCloud)
    square2 = patches.Rectangle((pCoords[0] * 32, pCoords[1] * 32), 50,50, color='BLUE')
    ax.add_patch(square2)
    fig.canvas.draw()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
'''


