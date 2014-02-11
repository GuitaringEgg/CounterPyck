import cv2, os
import numpy as np
from matplotlib import pyplot as plt

img_rgb = cv2.imread('ss.png')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

for image in os.listdir("images/"):
    template = cv2.imread(os.path.join("images/", image),0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    if zip(*loc[::-1]):
        print "Detected {}".format(image)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

cv2.imwrite('res.png',img_rgb)
