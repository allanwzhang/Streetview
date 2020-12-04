# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:05:00 2020

@author: Allan
"""
import csv

latlon = []
with open("data\PLUTOData.csv", 'r') as csvfile:
    csvL = csv.reader(csvfile) 
    for row in csvL:
        latlon.append(row)

print("doneLL")

business = []
with open("C:\Allan\Streetview\pythonCode\data\\businessData.csv", 'r') as csvfile:
    csvB = csv.reader(csvfile) 
    for row in csvB:
        business.append(row)

print("doneB")

li = 0
bi = 0

count = 0
data = []

while bi < len(business) and li < len(latlon):
    currB = business[bi]
    currL = latlon[li]
    if int(currB[0]) == int(currL[0]):
        data.append([currB[0], currL[1], currL[2], currB[1], currB[2], currB[3],
                     currB[4], currB[5], currB[6], currB[7], currB[8]])
        bi+=1
        li-=1
    if int(currL[0]) > int(currB[0]):
        count+=1
        bi+=1
    li+=1
 
print(count)
print(len(data))

with open('data\combineBusinessData.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for x in data:
            writer.writerow([x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10]])
