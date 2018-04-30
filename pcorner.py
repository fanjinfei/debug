import cv2
import numpy as np
import sys
import pylab
from matplotlib import pyplot as plt

import imageio #read video
from PIL import Image #read image
import rasl #image alignment

filename = sys.argv[1]

if False:
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # find Harris corners
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray,2,3,0.04)
    dst = cv2.dilate(dst,None)
    #ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
    ret, dst = cv2.threshold(dst,0.05*dst.max(),255,0)
    dst = np.uint8(dst)

    # find centroids
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # define the criteria to stop and refine the corners
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)

    # Now draw them
    print centroids,'\n', corners
    res = np.hstack((centroids,corners))
    print res
    res = np.int0(res)
    print res
    img[res[:,1],res[:,0]]=[0,0,255]
    img[res[:,3],res[:,2]] = [0,255,0]

    #cv2.imwrite(sys.argv[2],img)
    # corner detection
    fig = pylab.figure()
    pylab.imshow(img)
    pylab.show()


img = cv2.imread(filename,0)
#edges = cv2.Canny(img,100,200)
edges = cv2.Canny(img,50,100)

import pdb; pdb.set_trace()
plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
#plt.subplot(122),plt.imshow(edges,cmap = 'gray')
#edges = cv2.cvtColor(edges,cv2.COLOR_BGR2GRAY)
plt.subplot(122),plt.imshow(edges)
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()

