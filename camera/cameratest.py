import flycapture2 as fc2
import numpy as np
import cv2

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

# c = fc2.Context()
# c.connect(*c.get_camera_from_index(0))
#
# c.start_capture()

cap = cv2.VideoCapture(1)

while(True):
    # Capture frame-by-frame
    # im = fc2.Image()
    # c.retrieve_buffer(im)
    # frame = np.array(im)
    ret, frame = cap.read()

    # Our operations on the frame come here
    ## draw a diagonal line
    # frame = cv2.line(frame, (0,0), (frame.shape[1],frame.shape[0]), (255,0,0), 5)
    # draw a rect
    frame = cv2.rectangle(frame,
                          (int(frame.shape[1]/2 - 50), int(frame.shape[0]/2 - 50)),
                          (int(frame.shape[1]/2 + 50), int(frame.shape[0]/2 + 50)),
                          (0,255,0),
                          3)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
# c.stop_capture()
# c.disconnect()
cap.release()
cv2.destroyAllWindows()