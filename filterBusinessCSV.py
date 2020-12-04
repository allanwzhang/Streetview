# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 19:49:29 2020

@author: Allan
"""
import csv
        
def writeCSV(data):
    with open('data\businessData.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        #writer.writerow(["Business Name", "Business Name 2", "Address Building", "Address Street Name",
        #                 "Secondary Address Street Name", "Address City", "Address State", "Address ZIP",
        #                 "Latitude", "Longitude"])
        for x in data:
            writer.writerow([x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]])
            
data = []

with open("data\Legally_Operating_Businesses.csv", 'r') as csvfile:
    csvreader = csv.reader(csvfile) 
    for row in csvreader:
        if row[1] == "Business" and row[12] == "NY" and row[3] == "Active" and row[20] != "" and len(row[20]) == 10:
            data.append([row[20], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]])

data.sort(key=lambda x: x[0])

writeCSV(data)

#csv metadata:
#Business Name, Business Name 2, Address Building, Address Street Name
#Secondary Address Street Name, Address City, Address State, Address ZIP
#lat, lon