import time
from IDS_Camera import CameraDaemon
import os
# A simple generator function
def my_gen():
    counter = 0
    while True:
        yield counter
        counter = counter +1
        time.sleep(5)

# Using for loop
#for item in my_gen():
    #print(item)

CameraDaemon.retrieve_offset(30, 'Algorithm1')
CameraDaemon.offset_generator(30, 'Algorithm1')

