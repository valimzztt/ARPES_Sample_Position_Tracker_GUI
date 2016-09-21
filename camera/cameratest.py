import flycapture2 as fc2
import numpy as np
import cv2
import time

def test():
    print(fc2.get_library_version())
    c = fc2.Context()
    print(c.get_num_of_cameras())
    c.connect(*c.get_camera_from_index(0))
    print(c.get_camera_info())
    # c.set_video_mode_and_frame_rate(fc2,
    #         fc2.FRAMERATE_7_5)
    m, f = c.get_video_mode_and_frame_rate()
    print((m, f))
    # print c.get_video_mode_and_frame_rate_info(m, f)
    print((c.get_property_info(fc2.FRAME_RATE)))
    p = c.get_property(fc2.FRAME_RATE)
    print(p)
    c.set_property(**p)
    c.start_capture()
    im = fc2.Image()
    # print [np.array(c.retrieve_buffer(im)).sum() for i in range(80)]
    c.retrieve_buffer(im)
    a = np.array(im)
    print((a.shape, a.base))
    c.stop_capture()
    c.disconnect()

c = fc2.Context()
c.connect(*c.get_camera_from_index(0))

c.start_capture()

# cap = cv2.VideoCapture(1)

last = np.array([0])

while(True):
    # Capture frame-by-frame
    im = fc2.Image()
    c.retrieve_buffer(im)
    frame = np.array(im)
    # ret, frame = cap.read()

    # grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (3,3), 2)

    # Our operations on the frame come here
    canny= cv2.Canny(frame, 100, 150)
    minLineLength = 20
    maxLineGap = 10
    lines = cv2.HoughLinesP(canny, 1, np.pi/180, 100, minLineLength=minLineLength, maxLineGap=maxLineGap)
    circles = cv2.HoughCircles(frame, cv2.HOUGH_GRADIENT, 1, 10, param1=150)

    if(lines is not None):
        for line in lines:
            # print(lines)
            for x1,y1,x2,y2 in line:
                cv2.line(frame, (x1,y1), (x2,y2), 255, 2)

                circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 1, minDist=5, param1=150, minRadius=10, maxRadius=100)

    if(circles is not None):
        circles  = np.uint16(np.around(circles))
        print(circles)
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)

    # draw a rect
    frame = cv2.rectangle(frame,
                          (int(frame.shape[1]/2 - 50), int(frame.shape[0]/2 - 50)),
                          (int(frame.shape[1]/2 + 50), int(frame.shape[0]/2 + 50)),
                          (0,255,0),
                          3)

    # frame = cv2.rectangle(frame, (0,0), (100,100), (0,255, 0), 3)



    # Display the resulting frame
    cv2.imshow('frame',frame)
    cv2.imshow('canny edge', canny)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
c.stop_capture()
c.disconnect()
# cap.release()
cv2.destroyAllWindows()