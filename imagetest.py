import numpy as np
import cv2


# Capture image
images = []
images.append(cv2.imread('samples/examples/Gold_bullet+uvlamp_aligngold_alignlampvertical15290049-2016-07-19-101     444.png.png'))
images.append(cv2.imread('samples/examples/LiFeAsZn_aligned.png'))
images.append(cv2.imread('samples/examples/WTE2-2016-09-13-102234.png'))

img = np.hstack(tuple(images))


# Our operations on the frame come here
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
grey = cv2.medianBlur(grey, 9)

ret, thresh = cv2.threshold(grey, 60, 255, cv2.THRESH_BINARY)
# thresh = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, -3)

image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:

    area = cv2.contourArea(cnt)

    if(area > 500 and area < 1000):
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h

        diff_to_square = abs(aspect_ratio - 1)

        if(diff_to_square < 0.3):
            image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
            img = cv2.rectangle(img, (x,y), (x+w,y+h), (0, 255, 0), 2)


# Display the resulting frame
cv2.imshow('img', img)
cv2.imshow('thresh', thresh)

k = cv2.waitKey(0)

if k==27:
    cv2.destroyAllWindows()