# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 21:34:05 2020

@author: Jerry
"""

import matplotlib.pyplot as plt
import numpy as np

pano_id = "GlGveTEw-VSmN3mv_DVuKQ"

output_file = "C:/Allan/Streetview/dataCollection/" + pano_id

treeCoords = [[440, 148], [49, 137], [471, 141]]

data = plt.imread(output_file + ".jpeg")
fig, ax = plt.subplots(figsize=(30, 15), dpi=96)
ax.imshow(data, interpolation='none')

plt.show()

def onclick(event):
    xCoord = int(event.xdata) / 4.3128
    yCoord = int(event.ydata) / 4.3128
    minD = 99999999999999999
    for ar in treeCoords:
        dist = np.sqrt((xCoord - ar[0]) ** 2 + (yCoord  - ar[1]) ** 2)
        minD = min(minD, dist)
    print(minD)

cid = fig.canvas.mpl_connect('button_press_event', onclick)