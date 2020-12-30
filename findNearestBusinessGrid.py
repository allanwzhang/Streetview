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
import geopy.distance
import math

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
    
    
'''
grid = []

for i in range(271):
    for j in range(423):
        grid.append([])

PLUTOArray = csvToArray("data\PLUTOData.csv")

for i in range(len(PLUTOArray)):
    ar = PLUTOArray[i]
    curr = utm.from_latlon(float(ar[1]), float(ar[2]))
    x=int((curr[0]-581000)/100)
    y=int((curr[1]-4488500)/100)
    grid[y*271+x].append(i)
    
print("done")
writeCSV(grid, 'data\gridData.csv')

'''

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
        result.append(utm.from_latlon(float(curr[0]), float(curr[1]))[0:2])
    return result
    

def closestFootprint(latlon, store1, store2):
    if len(store2) == 4 or len(store1) == 4:
        return store1
    doorUTM = utm.from_latlon(float(latlon[0]), float(latlon[1]))[0:2]
    store1Edges = parseMultistring(store1[4])
    store2Edges = parseMultistring(store2[4])
    
    minDist = 9999999999
    for i in range(len(store1Edges)):
        curr = store1Edges[i]
        adj = store1Edges[(i+1)%len(store1Edges)]
        currDist = pDistance(doorUTM[0], doorUTM[1], curr[0], curr[1], adj[0], adj[1])
        if currDist < minDist:
            minDist = currDist
    
    for i in range(len(store2Edges)):
        curr = store2Edges[i]
        adj = store2Edges[(i+1)%len(store2Edges)]
        currDist = pDistance(doorUTM[0], doorUTM[1], curr[0], curr[1], adj[0], adj[1])
        if currDist < minDist:
            return store2
    return store1

def findNearestBusiness(latlon, businessArray):
    minDist2 = 99999999999
    minI2 = -1
    minDist = 999999999999
    minI = -1
    for i in range(len(businessArray)):
        ar = businessArray[i]
        dist = geopy.distance.distance([latlon[0], latlon[1]], [float(ar[1]), float(ar[2])]).km
        if dist < minDist:
            minDist2 = minDist
            minDist = dist
            minI2 = minI
            minI = i
        elif dist < minDist2:
            minDist2 = dist
            minI2 = i
    return closestFootprint(latlon, businessArray[minI], businessArray[minI2])

grid = csvToArray("data\gridData.csv")
doorCoordArray = csvToArray("data\latlon.csv")
PLUTOArray = csvToArray("data\PLUTOFootprint.csv")

print(len(PLUTOArray))

storeToDoor = []

for ar in doorCoordArray:
    if ar[3] == 'lat' or float(ar[3]) < 35 or float(ar[3]) > 45 or float(ar[4]) < -80 or float(ar[4]) > -70:
        continue
    curr = utm.from_latlon(float(ar[3]), float(ar[4]))
    #Add multiple squares
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
    result = findNearestBusiness([float(ar[3]), float(ar[4])], possible)

    
    added = False
    for store in storeToDoor:
        if store[2] == result[3]:
            store.append(ar[3])
            store.append(ar[4])
            added = True
    if not added:
        storeToDoor.append([result[1], result[2], result[3], ar[3], ar[4]])
    

writeCSV(storeToDoor, "data\storeToDoorFootprint.csv")
