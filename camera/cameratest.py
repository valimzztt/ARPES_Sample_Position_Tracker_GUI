import flycapture2 as fc2
import numpy as np

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

def setupCamera():
    print(fc2.get_library_version())
    c = fc2.Context()
    c.connect(*c.get_camera_from_index(0))

    # Custom format: set_format7_configuration(mode, x_offset, y_offset, width, height, pixel_format)
    # Currently only Mono colour is supported
    c.set_format7_configuration(fc2.MODE_0, 0, 0, 1280, 720, fc2.PIXEL_FORMAT_MONO8)

    print(c.get_camera_info())
    # c.set_video_mode_and_frame_rate(fc2,
    #         fc2.FRAMERATE_7_5)
    # c.set_video_mode_and_frame_rate(fc2.VIDEOMODE_1280x960RGB, fc2.FRAMERATE_15)
    m, f = c.get_video_mode_and_frame_rate()
    print(m, f)
    # print c.get_video_mode_and_frame_rate_info(m, f)
    print(c.get_property_info(fc2.FRAME_RATE))
    p = c.get_property(fc2.FRAME_RATE)
    print(p)
    c.set_property(**p)
    print(c.get_format7_configuration())
    return c


def imageLoop(context):
    c = context
    c.start_capture()
    im = fc2.Image()

    while(True):
        try:
            c.retrieve_buffer(im)
            a = np.array(im)
            print(a)
        except:
            c.stop_capture()
            c.disconnect()
            # report error and proceed
            raise






if __name__ == "__main__":

    try:
        c = setupCamera()
        imageLoop(c)
        im = fc2.Image()
        c.retrieve_buffer(im)
        a = np.array(im)

    except (KeyboardInterrupt, SystemExit):
        print('Loop exited')

