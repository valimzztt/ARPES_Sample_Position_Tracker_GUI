"""
Created on Thu May 13 10:36:16 2021

@author: valen
"""
import cv2
import math
import time
import numpy as np


class CorrelationCalculator(object):
    'TODO: class description'

    version = '0.1'

    def __init__(self, initial_frame, detection_threshold=0.01):
        self.initial_frame = np.float32(cv2.cvtColor(initial_frame, cv2.COLOR_BGR2GRAY))
        self.detection_threshold = detection_threshold

    def detect_phase_shift(self, current_frame):
        'returns detected sub-pixel phase shift between two arrays'
        self.current_frame = np.float32(cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY))
        shift = cv2.phaseCorrelate(self.initial_frame, self.current_frame)
        return shift


# implementation

import cv2
dict1 = {}
values = []
keys = range(1, 201)

for i in range(1, 201):
    img = cv2.imread(r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\data\image1.png")
    img = np.float32(img)
    img2 = cv2.imread(
        r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\data\image{}.png".format(i)
    img2 =np.float32(img2)

    obj = CorrelationCalculator(img)
    shift = obj.detect_phase_shift(img2)
    x_trasl = shift[0][0]
    print("Detected x pixel translation is: ", x_trasl)
    values.append(x_trasl)

dict1 = dict(zip(keys, values))
print(dict1)

with open('pixel_vs_displ.csv', 'w') as output:
    writer = csv.writer(output)
    for key, value in dict1.items():
        writer.writerow([key, value])



