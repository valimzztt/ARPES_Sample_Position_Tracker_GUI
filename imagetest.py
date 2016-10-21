import numpy as np
import cv2


# Capture image
images = []
# images.append(cv2.imread('samples/examples/Gold_bullet+uvlamp_aligngold_alignlampvertical15290049-2016-07-19-101     444.png.png'))
# images.append(cv2.imread('samples/examples/LiFeAsZn_aligned.png'))
images.append(cv2.imread('samples/examples/WTE2-2016-09-13-102234.png'))
# images.append(cv2.imread('samples/examples/data/Bi2Se3_laser_001.png'))
# images.append(cv2.imread('samples/examples/data/CAM_lamp_001.png')) # false positive
# images.append(cv2.imread('samples/examples/data/Graphene-2016-10-14-131848.png'))
# images.append(cv2.imread('samples/examples/data/Graphene-2016-10-15-154359.png'))
# images.append(cv2.imread('samples/examples/data/Graphene-2016-10-16-164806.png'))
# images.append(cv2.imread('samples/examples/data/Sr2IrO4 SIO_B1#3 th0 phi26-2016-10-18-134443.png'))
# images.append(cv2.imread('samples/examples/data/Sr2IrO4-2016-10-18-100803.png'))
# images.append(cv2.imread('samples/examples/data/SrIrO4-2016-10-18-111125.png'))

img = np.hstack(tuple(images))


# Our operations on the frame come here
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
grey = cv2.medianBlur(grey, 9)

ret, thresh = cv2.threshold(grey, 60, 255, cv2.THRESH_BINARY)
cv2.imshow('thresh', thresh)

# thresh = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, -3)

image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

matches = []
sides = []

for cnt in contours:

    area = cv2.contourArea(cnt)
    # print(area)

    if(area > 100 and area < 1000):
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h
        # print(aspect_ratio)

        diff_to_square = abs(aspect_ratio - 1)

        if(diff_to_square < 0.5):
            matches.append(cnt)
    elif (area > 12000):
        image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
        sides.append(cnt)


if len(sides) == 2:
    x1,y1,w1,h1 = cv2.boundingRect(sides[0])
    x2,y2,w2,h2 = cv2.boundingRect(sides[1])

    # print(x1)
    # print(x2)

    for cnt in matches:
        x, y, w, h = cv2.boundingRect(cnt)
        # print(x)
        if (x1 < x2 and x1 <= x <= x2) or (x2 < x1 and x2 <= x <= x1):
            image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

else:
    for cnt in matches:
        x, y, w, h = cv2.boundingRect(cnt)

        image = cv2.drawContours(image, [cnt], 0, (255, 255, 255), 3)
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)


# Display the resulting frame
cv2.imshow('img', img)
cv2.imshow('contour', thresh)

cv2.imwrite('samples/examples/sample_demo.png', img)

k = cv2.waitKey(0)

if k==27:
    cv2.destroyAllWindows()