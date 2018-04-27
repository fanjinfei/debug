import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import sys

img1 = cv.imread(sys.argv[1],0)          # queryImage
img2 = cv.imread(sys.argv[2],0) # trainImage

# Initiate ORB detector
orb = cv.ORB_create()
# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

# create BFMatcher object
bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
# Match descriptors.
matches = bf.match(des1,des2)
# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)
# Draw first 10 matches.
#img3 = cv.drawMatches(img1,kp1,img2,kp2,matches[:10], flags=2)
img3 = cv.drawMatches(img1,kp1,img2,kp2,matches[:10], 2)
plt.imshow(img3),plt.show()
