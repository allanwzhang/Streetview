# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 21:51:51 2020

@author: Allan
"""

import csv
        
def writeCSV(data):
    with open('data\PLUTOData.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for x in data:
            writer.writerow([x[0], x[1], x[2]])
            
data = []

with open("data\Primary_Land_Use_Tax_Lot_Output__PLUTO_.csv", 'r') as csvfile:
    csvreader = csv.reader(csvfile) 
    for row in csvreader:
        data.append([row[68], row[73], row[74]])

data.pop(0)
data.sort(key=lambda x: x[0])

writeCSV(data)

