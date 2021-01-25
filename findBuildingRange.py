# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:42:29 2021

@author: Allan
"""

import csv
import utm
import requests
import json
import geopy.distance
import math
import numpy as np

def csvToArray(fileName):
    data = []
    with open(fileName, 'r') as csvfile:
        csvreader = csv.reader(csvfile) 
        for row in csvreader:
            data.append(row)
    return data

def findIndex(x, y):
    return int((y-4488500)/100)*271+int((x-581000)/100)

def parseMultistring(polygon):
    polygon = polygon[16:-3]
    stringcoords = polygon.split(", ")
    result = []
    for ar in stringcoords:
        curr = ar.split(" ")
        if curr[0][0] == "(":
            curr[0] = curr[0][1:]
        if curr[1][-1] == ")":
            curr[1] = curr[1][:-1]
        result.append(utm.from_latlon(float(curr[1]), float(curr[0]))[0:2])
    return result

#https://stackoverflow.com/questions/64775547/extract-depthmap-from-google-street-view
def getHeading(lat, lon):
        url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2&callback=_xdc_._v2mub5"
        url = url.format(lat, lon)
        resp = requests.get(url, proxies=None)
        line = resp.text.replace("/**/_xdc_._v2mub5 && _xdc_._v2mub5( ", "")[:-2]
        jdata = json.loads(line)
        return jdata[1][5][0][1][2][0]

#https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
def pDistance(x, y, x1, y1, x2, y2):
  A = x - x1;
  B = y - y1;
  C = x2 - x1;
  D = y2 - y1;

  dot = A * C + B * D;
  len_sq = C * C + D * D;
  param = -1;
  if (len_sq != 0):
      param = dot / len_sq;

  xx=0.0
  yy=0.0

  if (param < 0):
    xx = x1
    yy = y1
  elif (param > 1):
    xx = x2
    yy = y2
  else:
    xx = x1 + param * C
    yy = y1 + param * D

  dx = x - xx
  dy = y - yy
  return math.sqrt(dx * dx + dy * dy)


def findSlope(coordA, coordB):
    return (coordA[1] - coordB[1]) / (coordA[0] - coordB[0])

def toxCoord(camCoord, coord, camAngle):
    slope = findSlope(camCoord, coord)
    angle = -1
    if slope > 0:
        if coord[0] > camCoord[0]:
            angle = np.rad2deg(np.arctan(slope))
        else:
            angle = 180 + np.rad2deg(np.arctan(slope))
    else:
        if coord[0] > camCoord[0]:
            angle = 360 + np.rad2deg(np.arctan(slope))
        else:
            angle = 180 + np.rad2deg(np.arctan(slope))
    angle = camAngle - angle
    if angle < 360:
        angle += 360
    if angle > 360:
        angle -= 360
    angle = (angle/360) * 16384
    return angle

def findRange(possible, camCoord, angle):
    slope = np.tan(np.deg2rad(angle))
    camUTM = utm.from_latlon(camCoord[0], camCoord[1])
    ranges = []
    for door in possible:
        if len(door) == 4:
            continue
        dist = geopy.distance.distance(camCoord, [float(door[1]), float(door[2])]).km
        if dist > 0.03: #50 m theshold
            continue
        storeEdges = parseMultistring(door[4])        
        minDist = 9999999999999
        result = []
        for i in range(len(storeEdges)):
            curr = storeEdges[i]
            adj = storeEdges[(i+1)%len(storeEdges)]
            if curr == adj:
                continue
            currSlope = findSlope(curr, adj)
            if abs(currSlope - slope) > 1:
                continue
            currDist = pDistance(camUTM[0], camUTM[1], curr[0], curr[1], adj[0], adj[1])
            if currDist < minDist:
                minDist = currDist
                result = [curr, adj]
        if len(result) == 2:
            camUTM = utm.from_latlon(camCoord[0], camCoord[1])
            xCoordA = toxCoord(camUTM, result[0], angle)
            xCoordB = toxCoord(camUTM, result[1], angle)
            #print(utm.to_latlon(result[0][0], result[0][1], 18, 'T'))
            #print(utm.to_latlon(result[1][0], result[1][1], 18, 'T'))
            #print(xCoordA, xCoordB)
            #print(result[0], result[1])
            ranges.append([min(xCoordA, xCoordB), max(xCoordA, xCoordB)]) 
        
    return ranges
            
def main(camCoord):
    #Local Files
    grid = csvToArray("data\Final\gridData.csv")
    PLUTOArray = csvToArray("data\Final\PLUTOFootprint.csv")
    
    print("done loading")
    
    curr = utm.from_latlon(camCoord[0], camCoord[1])
    
    surroundingI = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            currIndex = findIndex(curr[0]+i*100, curr[1]+j*100)
            if currIndex not in surroundingI:
                surroundingI.append(currIndex)
    
    possible = []
    for i in surroundingI:
        for bus in grid[i]:
            possible.append(PLUTOArray[int(bus)])
    
    angle = getHeading(camCoord[0], camCoord[1])
    angle = 270 - angle
    if angle < 0:
        angle += 360
    
    return findRange(possible, camCoord, angle)
    
camCoord = [40.7180441,-74.0048158]
print(main(camCoord))
        