# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 20:20:29 2020

@author: Allan
"""

import geopy.distance
import csv

def findNearestBusiness(latlon, businessArray):
    result = []
    minDist = 999999999999
    for ar in businessArray:
        if ar[8] == "" or ar[9] == "":
            continue
        dist = geopy.distance.distance([latlon[0], latlon[1]], [float(ar[8]), float(ar[9])]).km
        if dist < minDist:
            minDist = dist
            result = ar
    return result
    
def csvToArray(fileName):
    data = []
    with open(fileName, 'r') as csvfile:
        csvreader = csv.reader(csvfile) 
        for row in csvreader:
            data.append(row)
    return data

businessArray = csvToArray("businessData.csv")
print(findNearestBusiness([40.60923, -74.167], businessArray))