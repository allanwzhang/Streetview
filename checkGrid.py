# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 21:01:41 2021

@author: Jerry
"""


import numpy as np
import matplotlib.pyplot as plt

graph = np.load("grid.npy")

x = np.empty(2232300)
y = np.empty(2232300)

index=0
for i in range(len(graph)):
    if graph[i] == 1:
        x[index] = i % 4950
        y[index] = int(i/4950)
        index+=1
print(index)
'''
index = 0
for i in range(1200, 2200):
    for j in range(0, 2000):
        if graph[j*4950+i] == 1:
            x[index] = i
            y[index] = j
            index+=1
            #print(i,j)
print(index)
'''
plt.scatter(x, y)
plt.show()