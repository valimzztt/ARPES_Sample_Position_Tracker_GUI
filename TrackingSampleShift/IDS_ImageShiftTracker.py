from pyueye import ueye
import numpy as np
import time
import logging
import pytz
from Algorithms.Algorithm1 import phase_cross_correlation
from Algorithms.Algorithm2 import imregpoc
from ctypes import *
from scipy import ndimage

tz = pytz.timezone('America/Vancouver')


#---------------------------------------------------------------------------------------------------------------------------------------
#setup for te directory of the images
import datetime
from datetime import date

today_date =  date.today()

#---------------------------------------------------------------------------------------------------------------------------------------

#Variables
hCam = ueye.HIDS(0)             #0: first available camera;  1-254: The camera with the specified camera ID
sInfo = ueye.SENSORINFO()
cInfo = ueye.CAMINFO()
pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()
rectAOI = ueye.IS_RECT()
pitch = ueye.INT()
nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
bytes_per_pixel = int(nBitsPerPixel / 8)

bAOI_active = ueye.bool(False)                  # set active to use the AOI defined below
#---------------------------------------------------------------------------------------------------------------------------------------


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")

def check_ueye(func, *args, exp=ueye.IS_SUCCESS, raise_exc=True, txt=None):
    ret = func(*args)
    if not txt:
        txt = "{}: Expected {} but ret={}!".format(str(func), exp, ret)
    if ret != exp:
        if raise_exc:
            raise RuntimeError(txt)
        else:
            logging.critical(txt)

class ImageBuffer:
    memory_pointer = None
    memory_id = None
    width = None
    height = None
    bits_per_pixel = None

def get_bits_per_pixel(color_mode):
    formats = {ueye.IS_CM_SENSOR_RAW8: 8,
               ueye.IS_CM_SENSOR_RAW10: 16,
               ueye.IS_CM_SENSOR_RAW12: 16,
               ueye.IS_CM_SENSOR_RAW16: 16,

               ueye.IS_CM_MONO8: 8,
               ueye.IS_CM_MONO10: 16,
               ueye.IS_CM_MONO12: 16,
               ueye.IS_CM_MONO16: 16,

               ueye.IS_CM_RGB8_PLANAR: 24,
               ueye.IS_CM_RGB8_PACKED: 24,
               ueye.IS_CM_RGBA8_PACKED: 32,
               ueye.IS_CM_RGBY8_PACKED: 32,
               ueye.IS_CM_RGB10_PACKED: 32,

               ueye.IS_CM_RGB10_UNPACKED: 48,
               ueye.IS_CM_RGB12_UNPACKED: 48,
               ueye.IS_CM_RGBA12_UNPACKED: 64,

               ueye.IS_CM_BGR5_PACKED: 16,
               ueye.IS_CM_BGR565_PACKED: 16,
               ueye.IS_CM_BGR8_PACKED: 24,
               ueye.IS_CM_BGRA8_PACKED: 32,
               ueye.IS_CM_BGRY8_PACKED: 32,
               ueye.IS_CM_BGR10_PACKED: 32,

               ueye.IS_CM_BGR10_UNPACKED: 48,
               ueye.IS_CM_BGR12_UNPACKED: 48,
               ueye.IS_CM_BGRA12_UNPACKED: 64,

               ueye.IS_CM_UYVY_PACKED: 16,
               ueye.IS_CM_UYVY_MONO_PACKED: 16,
               ueye.IS_CM_UYVY_BAYER_PACKED: 16,
               ueye.IS_CM_CBYCRY_PACKED: 16
               }

    return formats[color_mode]

class minAOI:
    width = ueye.IS_SIZE_2D()
    height = ueye.IS_SIZE_2D()

def get_str_colormode(strcolor_mode):
    formats = {ueye.IS_CM_SENSOR_RAW8: "IS_CM_SENSOR_RAW8",
               ueye.IS_CM_SENSOR_RAW10: "IS_CM_SENSOR_RAW10",
               ueye.IS_CM_SENSOR_RAW12: "IS_CM_SENSOR_RAW12",
               ueye.IS_CM_SENSOR_RAW16: "IS_CM_SENSOR_RAW16",

               ueye.IS_CM_MONO8: "IS_CM_MONO8",
               ueye.IS_CM_MONO10: "IS_CM_MONO10",
               ueye.IS_CM_MONO12: "IS_CM_MONO12",
               ueye.IS_CM_MONO16: "IS_CM_MONO16",

               ueye.IS_CM_RGB8_PLANAR: "IS_CM_RGB8_PLANAR",
               ueye.IS_CM_RGB8_PACKED: "IS_CM_RGB8_PACKED",
               ueye.IS_CM_RGBA8_PACKED: "IS_CM_RGB8_PACKED",
               ueye.IS_CM_RGBY8_PACKED: "IS_CM_RGBY8_PACKED",
               ueye.IS_CM_RGB10_PACKED: "IS_CM_RGB10_PACKED",

               ueye.IS_CM_RGB10_UNPACKED: "IS_CM_RGB10_UNPACKED",
               ueye.IS_CM_RGB12_UNPACKED: "IS_CM_RGB12_UNPACKED",
               ueye.IS_CM_RGBA12_UNPACKED: "IS_CM_RGBA12_UNPACKED",

               ueye.IS_CM_BGR5_PACKED: "IS_CM_BGR5_PACKED",
               ueye.IS_CM_BGR565_PACKED: "IS_CM_BGR565_PACKED",
               ueye.IS_CM_BGR8_PACKED: "IS_CM_BGR8_PACKED",
               ueye.IS_CM_BGRA8_PACKED: "IS_CM_BGRA8_PACKED",
               ueye.IS_CM_BGRY8_PACKED: "IS_CM_BGRY8_PACKED",
               ueye.IS_CM_BGR10_PACKED: "IS_CM_BGR10_PACKED",

               ueye.IS_CM_BGR10_UNPACKED: "IS_CM_BGR10_UNPACKED",
               ueye.IS_CM_BGR12_UNPACKED: "IS_CM_BGR12_UNPACKED",
               ueye.IS_CM_BGRA12_UNPACKED: "IS_CM_BGRA12_UNPACKED",

               ueye.IS_CM_UYVY_PACKED: "IS_CM_UYVY_PACKED",
               ueye.IS_CM_UYVY_MONO_PACKED: "IS_CM_UYVY_MONO_PACKED",
               ueye.IS_CM_UYVY_BAYER_PACKED: "IS_CM_UYVY_BAYER_PACKED",
               ueye.IS_CM_CBYCRY_PACKED: "IS_CM_CBYCRY_PACKED"
               }

    return formats[strcolor_mode]

def mem_ptr():
    return ueye.c_mem_p()

def get_pitch(h_cam):
    x = ueye.int()
    y = ueye.int()
    bits = ueye.int()
    pitch = ueye.int()

    pc_mem = mem_ptr()
    pid = ueye.int()
    ueye.is_GetActiveImageMem(h_cam, pc_mem, pid)
    ueye.is_InquireImageMem(h_cam, pc_mem, pid, x, y, bits, pitch)

    return pitch

# chrono time to save
chrono_time = 10  # second

# ---------------------------------------------------------------------------------------------------------------------------------------
# path params to set on the camera
params_path = ueye.c_wchar_p("UI528xCP-C_conf.ini")

# Variables
# 0: first available camera;  1-254: The camera with the specified camera ID
hCam = ueye.HIDS(0)
sInfo = ueye.SENSORINFO()
cInfo = ueye.CAMINFO()
pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()
rectAOI = ueye.IS_RECT()
readminAOI = ueye.IS_SIZE_2D()
pitch = ueye.INT()
# 24: bits per pixel for color mode; take 8 bits per pixel for monochrome
nBitsPerPixel = ueye.INT(32)
channels = 3  # 3: channels for color mode(RGB); take 1 channel for monochrome
m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
bytes_per_pixel = int(nBitsPerPixel / 8)
# set the camera parammeter

# ---------------------------------------------------------------------------------------------------------------------------------------
print("START")
print()



# -----------------------------------------------------------
# Starts the driver and establishes the connection to the camera
# -----------------------------------------------------------
nRet = ueye.is_InitCamera(hCam, None)
if nRet != ueye.IS_SUCCESS:
    print("is_InitCamera ERROR")

# -----------------------------------------------------------
# Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
# -----------------------------------------------------------
nRet = ueye.is_GetCameraInfo(hCam, cInfo)
if nRet != ueye.IS_SUCCESS:
    print("is_GetCameraInfo ERROR")

# -----------------------------------------------------------
# You can query additional information about the sensor type used in the camera
# -----------------------------------------------------------
nRet = ueye.is_GetSensorInfo(hCam, sInfo)
if nRet != ueye.IS_SUCCESS:
    print("is_GetSensorInfo ERROR")

# -----------------------------------------------------------
#  Ensures to start with default parameter
# -----------------------------------------------------------
nRet = ueye.is_ResetToDefault(hCam)
if nRet != ueye.IS_SUCCESS:
    print("is_ResetToDefault ERROR")

# -----------------------------------------------------------
# Set display mode to DIB
# -----------------------------------------------------------
nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)

# -----------------------------------------------------------
#  request colormode
# -----------------------------------------------------------
iColorMode = ueye.is_SetColorMode(hCam, ueye.IS_GET_COLOR_MODE)
# determine the required bits per pixel

strColormode = get_str_colormode(iColorMode)

bits_per_pixel = ueye.INT(get_bits_per_pixel(iColorMode))
bytes_per_pixel = int(bits_per_pixel / 8)


# Set the right color mode
if int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
    # setup the color depth to the current windows setting
    ueye.is_GetColorDepth(hCam, nBitsPerPixel, m_nColorMode)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("IS_COLORMODE_BAYER: ", )
    print("\tm_nColorMode: \t\t", m_nColorMode)
    print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
    print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
    print()

elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
    # for color camera models use RGB32 mode
    m_nColorMode = ueye.IS_CM_BGRA8_PACKED
    nBitsPerPixel = ueye.INT(32)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("IS_COLORMODE_CBYCRY: ", )
    print("\tm_nColorMode: \t\t", m_nColorMode)
    print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
    print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
    print()

elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
    # for color camera models use RGB32 mode
    m_nColorMode = ueye.IS_CM_MONO8
    nBitsPerPixel = ueye.INT(8)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("IS_COLORMODE_MONOCHROME: ", )
    print("\tm_nColorMode: \t\t", m_nColorMode)
    print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
    print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
    print()

else:
    # for monochrome camera models use Y8 mode
    m_nColorMode = ueye.IS_CM_MONO8
    nBitsPerPixel = ueye.INT(8)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("else")


# ---------------------------------------------------------
# Prints out some information about the camera and the sensor
# ---------------------------------------------------------

# Can be used to set the size and position of an "area of interest"(AOI) within an image
nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
if nRet != ueye.IS_SUCCESS:
    print("is_AOI ERROR")

width = rectAOI.s32Width
height = rectAOI.s32Height

print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
print("Maximum image width:\t", width)
print("Maximum image height:\t", height)
print()


# ---------------------------------------------------------
# Set AOI
# AOI ON = bAOI_active(True)
# AOI OFF = bAOI_active(False) --> default settings from sensor
# ---------------------------------------------------------
if bAOI_active:


    check_ueye(ueye.is_AOI, hCam, ueye.IS_AOI_IMAGE_GET_SIZE_MIN, readminAOI, ueye.sizeof(readminAOI))

    # Get current pixel clock
    minAOI.width = readminAOI.s32Width
    minAOI.height = readminAOI.s32Height


    currentAOI = ueye.IS_RECT()
    currentAOI.s32X = 0
    currentAOI.s32Y = 0
    currentAOI.s32Width = 100
    currentAOI.s32Height = 100

    if (currentAOI.s32Width < minAOI.width or currentAOI.s32Height < minAOI.height):
        print("ERROR: \tThe selected image size of the AOI w= " + str(currentAOI.s32Width) + " h= "
              + str(currentAOI.s32Height) + " is smaller than the minimum image size of the sensor w= "
              + str(minAOI.width) + " h= " + str(minAOI.height))

        print("\t\tSetting the AOI to minimum sensor size w= " + str(minAOI.width) + " h= " + str(minAOI.height))
        currentAOI.s32Width = minAOI.width
        currentAOI.s32Height = minAOI.height

    print("AOI ON: " + str(currentAOI.s32Width) + " x " + str(currentAOI.s32Height))
else:

    currentAOI = ueye.IS_RECT()
    currentAOI.s32X = 0
    currentAOI.s32Y = 0
    currentAOI.s32Width = width
    currentAOI.s32Height = height
    print("AOI OFF: " + str(currentAOI.s32Width) + " x " + str(currentAOI.s32Height))

check_ueye(ueye.is_AOI, hCam, ueye.IS_AOI_IMAGE_SET_AOI, currentAOI, ueye.sizeof(currentAOI), raise_exc=False)

# ---------------------------------------------------------
# Pixel clock settingsq
# ---------------------------------------------------------
getpixelclock = ueye.UINT(0)
print("Pixel clock value is: {}".format(getpixelclock))
newpixelclock = ueye.UINT(0)
newpixelclock.value = 432
PixelClockRange = (ueye.int * 3)()

# Get pixel clock range
nRet = ueye.is_PixelClock(hCam, ueye.IS_PIXELCLOCK_CMD_GET_RANGE, PixelClockRange, ueye.sizeof(PixelClockRange))
print(nRet)
print(PixelClockRange)

if nRet == ueye.IS_SUCCESS:
    nPixelClockMin = PixelClockRange[0]
    nPixelClockMax = PixelClockRange[1]
    nPixelClockInc = PixelClockRange[2]


pc = (c_int * 1)(nPixelClockMax)
# Set default pixel clock
check_ueye(ueye.is_PixelClock, hCam, ueye.PIXELCLOCK_CMD.IS_PIXELCLOCK_CMD_SET, pc, ueye.sizeof(nPixelClockMax))
# Get current pixel clock
check_ueye(ueye.is_PixelClock, hCam, ueye.PIXELCLOCK_CMD.IS_PIXELCLOCK_CMD_GET, getpixelclock,
           ueye.sizeof(getpixelclock))

# ---------------------------------------------------------
# Framerate settings
# ---------------------------------------------------------
currentfps = ueye.c_double(0)
check_ueye(ueye.is_SetFrameRate, hCam,  ueye.c_double(15), currentfps)
print("Framerate is set to: " + str(currentfps) + "fps")

# ---------------------------------------------------------
# Exposure settings
# ---------------------------------------------------------
timeExp = ueye.DOUBLE(0)
check_ueye(ueye.is_Exposure, hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, timeExp, ueye.sizeof(timeExp))
print("Get Exposure :", timeExp)
timeExp = ueye.DOUBLE(0.124)
check_ueye(ueye.is_Exposure, hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, timeExp, ueye.sizeof(timeExp))
print("Set Exposure :", timeExp)
# ---------------------------------------------------------
# Create Imagequeue
# - allocate 3 ore more buffers depending on the framerate
# - initialize Imagequeue
# ---------------------------------------------------------
buffers = []
for y in range(3):
    buffers.append(ImageBuffer())

for x in range(len(buffers)):
    buffers[x].bits_per_pixel = bits_per_pixel  # RAW8
    buffers[x].height = currentAOI.s32Height  # sensorinfo.nMaxHeight
    buffers[x].width = currentAOI.s32Width  # sensorinfo.nMaxWidth
    buffers[x].memory_id = ueye.int(0)
    buffers[x].memory_pointer = ueye.c_mem_p()
    check_ueye(ueye.is_AllocImageMem, hCam, buffers[x].width, buffers[x].height, buffers[x].bits_per_pixel,
               buffers[x].memory_pointer, buffers[x].memory_id)
    check_ueye(ueye.is_AddToSequence, hCam, buffers[x].memory_pointer, buffers[x].memory_id)

check_ueye(ueye.is_InitImageQueue, hCam, ueye.c_int(0))


# ---------------------------------------------------------
# Using Software Trigger mode
# ---------------------------------------------------------
check_ueye(ueye.is_SetExternalTrigger, hCam, ueye.IS_SET_TRIGGER_SOFTWARE)

# ---------------------------------------------------------
# Activates the camera's live video mode (free run mode)
# ---------------------------------------------------------
nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)
if nRet != ueye.IS_SUCCESS:
    print("is_CaptureVideo ERROR")


# ---------------------------------------------------------------------------------------------------------------------------------------
start_chrono = time.time()
counter = 0

# # Continuous image display
import cv2

# importing os module
import os

counter = 0
imageinfo = ueye.UEYEIMAGEINFO()
print(imageinfo)
sensorinfo = ueye.SENSORINFO()
current_buffer = ueye.c_mem_p()
current_id = ueye.int()
Temp_buffer = ueye.c_mem_p()
memories_buffer = []
m_MissingTrgCounter = ueye.int(0)
test = (nBitsPerPixel + 7) / 8
index = 0
i= 0
reference_images = []
reference_images_laplace = []
alg1_x_pixel_offset =[]
alg1_y_pixel_offset = []
alg2_x_pixel_offset =[]
alg2_y_pixel_offset =[]
alg2_lp_x_pixel_offset=[]
alg2_lp_y_pixel_offset=[]
alg3_x_pixel_offset =[]
alg3_y_pixel_offset =[]
alg4_x_pixel_offset =[]
alg4_y_pixel_offset =[]
alg4_lp_x_pixel_offset =[]
alg4_lp_y_pixel_offset =[]
indexes =[]
time_images =[]



# while (nRet == ueye.IS_SUCCESS) and (counter < chrono_time):
while True:
    start_time = time.time()
    counter = start_time - start_chrono
    nret = ueye.is_WaitForNextImage(hCam, 1000, current_buffer, current_id)
    if nret == ueye.IS_SUCCESS:
        logging.debug("is_WaitForNextImage, Status IS_SUCCESS: {}".format(nret))
        check_ueye(ueye.is_GetImageInfo, hCam, current_id, imageinfo, ueye.sizeof(imageinfo))
        # check_ueye(ueye.is_GetImageMemPitch(hCam, pitch))
        getpitch = get_pitch(hCam)

        counter = counter + 1
        index = index + 1

        array = ueye.get_data(current_buffer, currentAOI.s32Width, currentAOI.s32Height, nBitsPerPixel, getpitch,
                              copy=False)
        frame = np.reshape(array, (currentAOI.s32Height.value, currentAOI.s32Width.value, bytes_per_pixel))
        # cv2.imwrite("frame" + str(counter) + ".png", frame)
        # saving IMG
        # ...resize the image by a half
        frame = cv2.resize(frame, (1024, 768), fx=0.5, fy=0.5)
        if counter < 1.1:
            reference_images.append(frame)
        # Algorithm1
        alg1_offset = phase_cross_correlation(reference_images[0], frame, upsample_factor=100)[0]
        alg1_x_pixel_offset.append(alg1_offset[1])
        alg1_y_pixel_offset.append(alg1_offset[0])
        print(alg1_offset[1])

        # Algorithm 3
        #from skimage.registration import phase_cross_correlation

        #shifted, error, diffphase = phase_cross_correlation(reference_images[0], frame, upsample_factor=200)
        #alg3_x_pixel_offset.append(shifted[1])
        #alg3_y_pixel_offset.append(shifted[0])


        # using the Laplacian operator
        #frame_lp = ndimage.gaussian_laplace(frame, sigma=2)
        # Algorithm2 with laplacian operator
        #alg2_offset_lp = imregpoc(reference_images_laplace[0], frame_lp)
        #alg2_lp_x_pixel_offset.append(-alg2_offset_lp.param[0])
        #alg2_lp_y_pixel_offset.append(-alg2_offset_lp.param[1])
        # Algorithm 4 with laplacian operator
        #alg4_offset_lp = cv2.phaseCorrelate(reference_images_laplace[0], frame_lp)[0]
        #alg4_lp_x_pixel_offset.append(-alg4_offset_lp[0])
        #alg4_lp_y_pixel_offset.append(-alg4_offset_lp[1])

        # cv2.imwrite("frame" + str(counter) + ".png", frame)
        date_string = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S_%f")
        time_image = datetime.datetime.strptime(date_string,'%m_%d_%Y_%H_%M_%S_%f')
        time_images.append(time_image)

        indexes.append(index)

        # ---------------------------------------------------------------------------------------------------------------------------------------
        # Print FPS hereqqq
        # print('FPS: ' , FPS)
        #print("FPS: ", int(1.0 / (time.time() - start_time)))

        check_ueye(ueye.is_UnlockSeqBuf, hCam, current_id, current_buffer)
        logging.debug("is_UnlockSeqBuf, current_id: {}".format(current_id))

    if nret == ueye.IS_TIMED_OUT:
        logging.debug("is_WaitForNextImage, Status IS_TIMED_OUT: {}".format(nret))
        logging.error("current_buffer: {}".format(current_buffer))
        logging.error("current_id: {}".format(current_id))
        # check_ueye(ueye.is_UnlockSeqBuf, hCam, current_id, current_buffer)

    if nret == ueye.IS_CAPTURE_STATUS:
        logging.debug("is_WaitForNextImage, IS_CAPTURE_STATUS: {}".format(nret))

        CaptureStatusInfo = ueye.UEYE_CAPTURE_STATUS_INFO()
        check_ueye(ueye.is_CaptureStatus, hCam, ueye.IS_CAPTURE_STATUS_INFO_CMD_GET, CaptureStatusInfo,
                   ueye.sizeof(CaptureStatusInfo))

        missedTrigger = ueye.ulong(0)
        TriggerCnt = ueye.ulong()  # IS_EXT_TRIGGER_EVENT_CNT
        missedTrigger = ueye.is_CameraStatus(hCam, ueye.IS_TRIGGER_MISSED, ueye.IS_GET_STATUS)
        m_MissingTrgCounter += missedTrigger

        logging.error("current_buffer: {}".format(current_buffer))
        logging.error("current_id: {}".format(current_id))

    if index > 334800:
        # ---------------------------------------------------------------------------------------------------------------------------------------
        import csv
        row_index = 0
        with open('pixel_vs_displ.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data = list(
                zip(indexes, alg1_x_pixel_offset, alg1_y_pixel_offset, time_images))
            writer.writerow(["Image Index", "Alg 1 x pixel offset","Alg 1 y pixel offset", "Image time taken"])
            for row in data:
                row = list(row)
                writer.writerow(row)
                row_index = row_index + 1

        os.rename(r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\pixel_vs_displ.csv",
                  r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\Vibrations_0817\vibration_data.csv")

        break


    elapsed_time = time.time() - start_time


# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)

# Disables the hCam camera handle and releases the data structures and memory acreas taken up by the uEye camera
ueye.is_ExitCamera(hCam)

# Destroys the OpenCv windows
cv2.destroyAllWindows()

print()
print("END")

