import cv2
import numpy as np
import image_restoration_tools

imlist_stb =[]
for i in range(1, 201):
    img = cv2.imread(r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\data\image1.png")
    img2 = cv2.imread(r"C:\Users\valmzztt.stu\My Python Scripts\Thorlabs Camera\PyuEye\data\image{}.png".format(i))

    img_denoised = np.float32(restoration.denoise_tv_chambolle(img.astype('uint16'), weight=0.1, multichannel=True)) #ref
    img2_denoised = np.float32(restoration.denoise_tv_chambolle(img2.astype('uint16'), weight=0.1, multichannel=True))
    # TODO: set window around phase correlation
    dp = cv2.phaseCorrelate(img_denoised, img2_denoised)
    cx = cx - dp[0]
    cy = cy - dp[1]
    xform = np.float32([[1, 0, cx], [0, 1, cy]])
    im_stb = cv2.warpAffine(im.astype('float32'), xform, dsize=(im_denoised.shape[1], im_denoised.shape[0]))
    imlist_stb.append(imclipper(im_stb,clip))
print(imlist_stb)