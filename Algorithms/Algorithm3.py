"""
Created on Thu May 13 09:33:26 2021

@author: valen
"""
import matplotlib.pyplot as plt
import cv2
import numpy as np
from skimage import color, io, data
from skimage.io import imread, imshow
from skimage.registration import phase_cross_correlation
from skimage.transform import rescale, resize, downscale_local_mean
from skimage.feature import register_translation
from scipy.ndimage import fourier_shift, shift

dicts = {}
keys = range(1, 201)
values = []

for i in range(1, 201):
    image = io.imread(
        r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\data\image1.png", as_gray = True)
    offset_image = io.imread(r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\data\image{}.png".format(i), as_gray=True)

   # subpixel precision
    # Upsample factor 100 = images will be registered to within 1/100th of a pixel.
    # Default is 1 which means no upsampling.
    shifted, error, diffphase = phase_cross_correlation(image, offset_image, upsample_factor=100)
    x_trasl = shifted[1]
    y_trasl = shifted[0]
    shifted = (x_trasl, y_trasl)
    values.append(-x_trasl)
    print(f"Detected subpixel offset (x, y): {shifted}")

dict1 = dict(zip(keys, values))
print(dict1)

import csv

with open('pixel_vs_displ.csv', 'w') as output:
    writer = csv.writer(output)
    for key, value in dict1.items():
        writer.writerow([key, value])

import os

os.rename(r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\Algorithms\pixel_vs_displ.csv",
          r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\pixel_offset_alg3.csv")


