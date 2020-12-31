# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 21:03:55 2020

@author: Allan
"""

#Grid of NYC: UTM 18N
#Bottom left: 581000 4488500
#Top Right: 608100 4530800
#Dimensions: 271x423 of (100x100 meter squares)

#UTM to Latitude Longitude: http://pypi.python.org/pypi/utm
#https://stackoverflow.com/questions/6778288/lat-lon-to-utm-to-lat-lon-is-extremely-flawed-how-come

import csv
import utm
import math
import geopy.distance
import numpy as np

def csvToArray(fileName):
    data = []
    with open(fileName, 'r') as csvfile:
        csvreader = csv.reader(csvfile) 
        for row in csvreader:
            data.append(row)
    return data

def writeCSV(data, fileName):
    with open(fileName, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for ar in data:
            writer.writerow(ar)
            
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

def magnitude(vector):
   return np.sqrt(np.dot(np.array(vector),np.array(vector)))

def norm(vector):
   return np.array(vector)/magnitude(np.array(vector))

def closestFootprint(latlon, store1, store2):
    doorUTM = utm.from_latlon(float(latlon[0]), float(latlon[1]))[0:2]
    store1Edges = parseMultistring(store1[4])
    store2Edges = parseMultistring(store2[4])
    
    minDist = 9999999999
    x = []
    y = []
    for i in range(len(store1Edges)):
        curr = store1Edges[i]
        adj = store1Edges[(i+1)%len(store1Edges)]
        currDist = pDistance(doorUTM[0], doorUTM[1], curr[0], curr[1], adj[0], adj[1])
        if currDist < minDist:
            minDist = currDist
            x = curr
            y = adj
    
    for i in range(len(store2Edges)):
        curr = store2Edges[i]
        adj = store2Edges[(i+1)%len(store2Edges)]
        currDist = pDistance(doorUTM[0], doorUTM[1], curr[0], curr[1], adj[0], adj[1])
        if currDist < minDist:
            minDist = currDist
            x = curr
            y = adj
    slope = (y[1] - x[1]) / (y[0] - x[0])
    angle = np.rad2deg(np.arctan(slope))
    #print(utm.to_latlon(*(x[0], x[1], 18, 'T')))
    #print(utm.to_latlon(*(y[0], y[1], 18, 'T')))
    return angle

def nearestBusinessAngle(coords, possible):
    minDist2 = 99999999999
    minI2 = -1
    minDist = 999999999999
    minI = -1
    for i in range(len(possible)):
        ar = possible[i]
        if len(possible[i]) == 4:
            continue
        dist = geopy.distance.distance(coords, [float(ar[1]), float(ar[2])]).km
        if dist < minDist:
            minDist2 = minDist
            minDist = dist
            minI2 = minI
            minI = i
        elif dist < minDist2:
            minDist2 = dist
            minI2 = i
    return closestFootprint(coords, possible[minI], possible[minI2])

def findDoorCoords(coords, angle, possible):
    minDist = 999999999
    result = []
    doorUTM = utm.from_latlon(float(coords[0]), float(coords[1]))[0:2]
    for ar in possible:
        if len(ar) == 4:
            continue
        storeEdges = parseMultistring(ar[4])
        for i in range(len(storeEdges)):
            curr = storeEdges[i]
            adj = storeEdges[(i+1)%len(storeEdges)]
            #print(curr, adj, doorUTM, angle)
            intersect = lineRayIntersectionPoint(doorUTM, [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))], curr, adj)
            if len(intersect) == 0:
                continue
            currDist = np.sqrt((intersect[0] - doorUTM[0])**2+(intersect[1]-doorUTM[1])**2)
            if currDist < minDist:
                minDist = currDist
                result = intersect
    return result

#https://stackoverflow.com/questions/14307158/how-do-you-check-for-intersection-between-a-line-segment-and-a-line-ray-emanatin

def lineRayIntersectionPoint(rayOrigin, rayDirection, point1, point2):
    # Convert to numpy arrays
    rayOrigin = np.array(rayOrigin, dtype=np.float)
    rayDirection = np.array(norm(rayDirection), dtype=np.float)
    point1 = np.array(point1, dtype=np.float)
    point2 = np.array(point2, dtype=np.float)

    # Ray-Line Segment Intersection Test in 2D
    # http://bit.ly/1CoxdrG
    v1 = rayOrigin - point1
    v2 = point2 - point1
    v3 = np.array([-rayDirection[1], rayDirection[0]])
    t1 = np.cross(v2, v1) / np.dot(v2, v3)
    t2 = np.dot(v1, v3) / np.dot(v2, v3)
    if t1 >= 0.0 and t2 >= 0.0 and t2 <= 1.0:
        return rayOrigin + t1 * rayDirection
    return []

grid = csvToArray("data\Final\gridData.csv")
PLUTOArray = csvToArray("data\Final\PLUTOFootprint.csv")

camCoord = [40.7180441,-74.0048158]

doorCoord = [3993, 4470]

curr = utm.from_latlon(camCoord[0], camCoord[1])

surroundingI = []
for i in range(-1, 2):
    currIndex = findIndex(curr[0]+i*50, curr[1])
    if currIndex not in surroundingI:
        surroundingI.append(currIndex)
    currIndex = findIndex(curr[0], curr[1]+i*50)
    if currIndex not in surroundingI:
        surroundingI.append(currIndex)
    
possible = []
for i in surroundingI:
    for bus in grid[i]:
        possible.append(PLUTOArray[int(bus)])

angle = nearestBusinessAngle(camCoord, possible)
if angle < 0:
    angle = 180 + angle
cangle = (doorCoord[0] / 16384) * 360
angle = angle - cangle
if angle < 0:
    angle += 360

result = findDoorCoords(camCoord, angle, possible)
toLL = (result[0], result[1], 18, 'T')
print(utm.to_latlon(*toLL))



