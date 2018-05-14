import sys, math
import time
import numpy as np
import heapq
import pylab
import imageio #read video
from PIL import Image #read image
import cv2
import rasl #image alignment

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from CannyEdge.utils import to_ndarray
from CannyEdge.core import (gs_filter, gradient_intensity, suppression,
                            threshold, tracking)

numpy = np
# A map of rgb points in your distribution
# [distance, (r, g, b)]
# distance is percentage from left edge
heatmap = [
    [0.0, (0, 0, 0)],
    [0.20, (0, 0, .5)],
    [0.40, (0, .5, 0)],
    [0.60, (.5, 0, 0)],
    [0.80, (.75, .75, 0)],
    [0.90, (1.0, .75, 0)],
    [1.00, (1.0, 1.0, 1.0)],
]

#revese heatmap
#heatmap = heatmap[:-3]

def rgb2gray(R,G,B):
    return 0.21*R + 0.72*G + 0.07*B

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def pixel(x, width=100, map=[], spread=1):
    width = float(width)
    r = sum([gaussian(x, p[1][0], p[0] * width, width/(spread*len(map))) for p in map])
    g = sum([gaussian(x, p[1][1], p[0] * width, width/(spread*len(map))) for p in map])
    b = sum([gaussian(x, p[1][2], p[0] * width, width/(spread*len(map))) for p in map])
    return min(1.0, r), min(1.0, g), min(1.0, b)

def gradient_color_demo():
    width = 1000
    im = Image.new('RGB', (width, 62))
    ld = im.load()

    for x in range(im.size[0]):
        r, g, b = pixel(x, width=width, map=heatmap)
        r, g, b = [int(256*v) for v in (r, g, b)]
        #r = int(gaussian(x, 158.8242, 201, 87.0739) + gaussian(x, 158.8242, 402, 87.0739))
        #g = int(gaussian(x, 129.9851, 157.7571, 108.0298) + gaussian(x, 200.6831, 399.4535, 143.6828))
        #b = int(gaussian(x, 231.3135, 206.4774, 201.5447) + gaussian(x, 17.1017, 395.8819, 39.3148))
        for y in range(im.size[1]):
            ld[x, y] = (r, g, b)
    fig = pylab.figure()
    pylab.imshow(im)
    pylab.show()

len_d = 60.0 #mm, PS4 eye
focus = 15.0 #mm
center_offset = 5
#^panasonic 3D parameter

#PS4 eye parameter: len_d=80.0mm focus=4.0mm
len_d=80.0
pixel_ratio=100.0 #each pix distance?
focus=4.0*100 #100: pixel->ratio
center_offset = -0.2

max_delta = 100 # delta = lend_d*focus/minimum_distance 30CM for PS4 eye

def calculate_focus(w, h, x1, x2, len_d, d): #from manually marked points to camera focus_length
    x_off_center = -0.2
    focus = 0
    x1 = abs(x1 - w/2 +x_off_center ) 
    x2 = abs(x2 - w/2 -x_off_center )
    if x2>x1: #swap, side same, not in the middle
        x1,x2=x2,x1
    focus = d/len_d*(x1-x2)
    print "focus lenght {0:.2f}mm, {1} {2} {3}".format(focus, x1, x2, (x1-x2))
    return focus
    
def calculate_distance(w, h, x1, x2, len_d, focus, x_off_center, verbose=False): #from manually marked points to distance
    x1 = (x1 - w/2 +x_off_center ) #left
    x2 = (x2 - w/2 -x_off_center ) #right
    delta = abs(x1-x2)
    d = len_d*focus/delta
    if verbose:
        print "distance lenght {0:.2f}mm, {1} {2} {3}".format(d, x1, x2, delta)
    return d

def calculate_pos(w, h, x1, y1, focus, z, verbose=False): #from 
    x = z/focus*(x1-w/2 +center_offset)
    y = z/focus*(y1-h/2)
    if verbose:
        print "pos xyz {0:.2f}mm, {1:.2f} {2:.2f}".format(x, y, z)
    return x,y,z

def normalize_px(px, w, h):
    px2 = numpy.empty((w, h))
    mx1, mx2=0,0
    for i in range(w):
        for j in range(h):
            mx2 = max(mx2, px[i][j])
            mn1 = min(mx1, px[i][j])
    for i in range(w):
        for j in range(h):
            px2[i][j] = (px[i][j]-mn1)/(mx2-mn1)*255.0
    return px2

def normalize_im(px, w, h):
    mx1, mx2=0,0
    for i in range(w):
        for j in range(h):
            mx2 = max(mx2, px[i,j])
            mn1 = min(mx1, px[i,j])
    for i in range(w):
        for j in range(h):
            px[i,j] = (px[i,j]-mn1)/(mx2-mn1)*255.0
    return px

lt_cache = numpy.empty((640, 400))
rg_cache = numpy.empty((640, 400))

def calculate_diff2(pix1, pix2, x1, y1, x2, y2, size=9): #9X9 square, SAD- sum of absolute difference
    d = 0
    for i in range(size):
        for j in range(size):
            d += abs(pix1[x1+i, y1+j] - pix2[x2+i, y2+j])
    return d, 0 #histogram diff?

def calculate_diff3(pix1, pix2, x1, y1, x2, y2, w=9, h =9): #rectangle, SAD- sum of absolute difference
    d = 0
    for i in range(w):
        for j in range(h):
            d += abs(pix1[x1+i, y1+j] - pix2[x2+i, y2+j])**2
    return d, 0 #histogram diff?

#input: left/right image, left p1(x1,y1), y_offset + y1 = y2
#output:match p2(x2,y2), val(confidence)
lf_cache = numpy.empty((640, 400))
rg_cache = numpy.empty((640, 400))
def calculate_match(px1, px2, x1, y1, y_offset, edge=10, max_right=100, verbose=False): 
    w,h = 640,400
    #edge = 10 #2*edge+1 = block size
    bsz = 2*edge +1
    x2, y2 = x1, y1+y_offset
    val = 0.0
    threshold = 0.0 #mininum matching
    res = []
    max_shift = min(max_right, x1-edge-1)

    if lt_cache[x1][y1] == 0:
        for l in range(y1-edge, y1+edge):
            for m in range(x1-edge, x1+edge):
                lt_cache[x1][y1] += px1[m, l] #block average

    win_h = 3
    for i in range(max_shift):
        if rg_cache[x1-i][y2] == 0:
            for l in range(y2-edge, y2+edge):
                for m in range(x1-i-edge, x1-i+edge):
                    rg_cache[x1-i][y2] += px2[m, l] #block average
        
        if abs(lt_cache[x1][y1] - rg_cache[x1-i][y2]) > 5000:
            res.append([i, 7000, 0])
            continue
        #sad, hd = calculate_diff2(px1, px2, x1-edge, y1-edge, x1-i-edge, y2-edge, bsz)
        sad, hd = calculate_diff3(px1, px2, x1-edge, y1-1, x1-i-edge, y2-1, bsz, 3)
        res.append([i, sad, hd])
        if sad < 2000 and len(res)>2:
            break
    #res.sort(key=lambda x:x[1])
    if verbose:
        res = heapq.nsmallest(5, res, key=lambda x:x[1])
        print res[:5]
    else:
        res = heapq.nsmallest(5, res, key=lambda x:x[1])
    i,val, _ = res[0]

    di = 0
    for k in range(2):
        di += res[k][0]
    di = int(di/2.0)
    if abs(di - res[0][0]) >2: #too explicit
        di = res[0][0]
    x2 = x1-di

    if verbose:
        print "match left xy {0:.2f}/{1:.2f} to right {2:.2f}/{3:.2f}, val {4:.2f}".format(x1, y1, x2, y2, val)
    if len(res) >3 and abs(res[3][0]- res[0][0])/(res[0][0]+1.0) < 0.1:
        return None, None, None
    return x2,y2,val

#ouput 3D PC, zero in left lens
def match_lr(em1, px1, px2, w, h, y_offset, edge=10):
    #match each of the p1 in px1 to p2 in px2, sort them in order
    #do not calculate the edge size(10)
    res = []
    count = 0
    count_e = 0
    pr_t = time.time()
    for j in range(16, h-edge-2):
        for i in range(14, w-edge-2):
            continue
            # very slow on python cpu
            for l in range(j-edge, j+edge):
                for m in range(i-edge, i+edge):
                    lt_cache[i][j] += px1[m, l] #block average
                    rg_cache[i][j] += px2[m, l]

    for j in range(16, h-edge-2):
        for i in range(14, w-edge-2):
            count += 1
            if count %10000 == 0:
                now = time.time()
                print count, "{0:.2f}".format(now-pr_t)
                pr_t = now
            if em1[j][i] == 0: continue
            count_e += 1
            mi, mj, val = calculate_match(px1, px2, i, j, y_offset, edge, 100) #100
            if val > 6000: continue
            if not mi: continue
            res.append([i, j, mi, mj, val])
    print 'count edge points', count_e
    return res

def draw2(ps):
    point  = np.array([1, 2, 3])
    normal = np.array([1, 1, 2])

    # a plane is a*x+b*y+c*z+d=0
    # [a,b,c] is the normal. Thus, we have to calculate
    # d and we're set
    d = -point.dot(normal)

    # create x,y
    xx, yy = np.meshgrid(range(10), range(10))

    # calculate corresponding z
    z = (-normal[0] * xx - normal[1] * yy - d) * 1. /normal[2]

    # Create the figure
    fig = plt.figure()

    # Add an axes
    ax = fig.add_subplot(111,projection='3d')

    # plot the surface
    #ax.plot_surface(xx, yy, z, alpha=0.2)

    # and plot the point 
    ax.scatter(0 , 0, 0,  color='red')
    for point2 in ps:
        #ax.scatter(point2[0]/100 , point2[1]/100 , point2[2]/100,  color='green')
        #ax.scatter(point2[0]/100 , point2[1]/100 , point2[2]/100, s=.5, cmap='hot')
        r, g, b = pixel(point2[2]/100, width=30, map=heatmap) #max 5.0meter away
        r, g, b = [int(256*v) for v in (r, g, b)]
        color = (r,g,b)
        ax.scatter(point2[0]/100 , point2[1]/100 , point2[2]/100, s=1.5, cmap=heatmap)
    ax.view_init(elev=45.)
    #for angle in range(0, 360):
    #    ax.view_init(30, angle)
    #    plt.draw()
    #    plt.pause(.001)

def get_edges(img_file, sigma, t, T):
    img = to_ndarray(img_file)
    img = gs_filter(img, sigma)
    img, D = gradient_intensity(img)
    img = suppression(img, D)
    img, weak = threshold(img, t, T)
    img = tracking(img, weak)
    return img

def detect_blob(frame):
    # Switch image from BGR colorspace to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # define range of purple color in HSV
    purpleMin = (115,50,10)
    purpleMax = (160, 255, 255)
    purpleMin = (150,150,150)
    purpleMax = (255, 255, 255)
    
    # Sets pixels to white if in purple range, else will be set to black
    mask = cv2.inRange(hsv, purpleMin, purpleMax)
    
    # Bitwise-AND of mask and purple only image - only used for display
    res = cv2.bitwise_and(frame, frame, mask= mask)

#    mask = cv2.erode(mask, None, iterations=1)
    # commented out erode call, detection more accurate without it

    # dilate makes the in range areas larger
    mask = cv2.dilate(mask, None, iterations=1)    
    
    # Set up the SimpleBlobdetector with default parameters.
    params = cv2.SimpleBlobDetector_Params()
     
    # Change thresholds
    params.minThreshold = 0;
    params.maxThreshold = 256;
     
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 30
     
    # Filter by Circularity
    '''
    params.filterByCircularity = True
    params.minCircularity = 0.1
     
    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.5
     
    # Filter by Inertia
    params.filterByInertia =True
    params.minInertiaRatio = 0.5
    '''
     
    detector = cv2.SimpleBlobDetector_create(params)
    
    # Detect blobs.
    reversemask=255-mask
    keypoints = detector.detect(reversemask)
    if keypoints:
        print "found %d blobs" % len(keypoints)
        if len(keypoints) > 4:
            # if more than four blobs, keep the four largest
            keypoints.sort(key=(lambda s: s.size))
            keypoints=keypoints[0:3]
    else:
        print "no blobs"
 
    # Draw green circles around detected blobs
    im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
    # open windows with original image, mask, res, and image with keypoints marked
    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)     
    cv2.imshow("Keypoints for", im_with_keypoints)

    k = cv2.waitKey(20000)
    cv2.destroyAllWindows()
    return None

#too slow for pixel matching
#try to match large block
def mblob_detect(frame): #detect large 20X20 sub-block similarity
    pass

def image_read(show=False):
    im1 = Image.open('/tmp/a.jpg') #left
    e_im1 = get_edges('/tmp/a.jpg', 1.4, 20, 40) #left
    c = 0
    for i in range(400):
        for j in range(640):
            if e_im1[i][j] != 0:
                c +=1 
    print (c)
    

    if False:
        orig_img = cv2.imread('/tmp/a.jpg')
        frame=cv2.GaussianBlur(orig_img, (3, 3), 0)
        return detect_blob(frame)
        
    
    im2 = Image.open('/tmp/b.jpg') #left
    pix1, pix2 = im1.load(), im2.load()

    #test calibration point (X/Y revert with imageio), horizion-X
    pix1[267,264]=(0,255,0) #marker green
    pix2[240,260]=(0,255, 0) #marker blue
    
    #fl = calculate_focus(640.0, 400.0, 267, 240, 80.0, 1200.0) #manual measure distance 120.0CM, len_d=8.0CM
    calculate_distance(640.0, 400.0, 267, 240, 80.0, 400.0, -0.2) # (bed pole)
    x,y,z = calculate_pos(640.0, 400.0, 267, 264, 400.0, 1203.0) #
    p1 = [x,y,z]
    
    print ''
    d2 = calculate_distance(640.0, 400.0, 318, 305, 80.0, 400.0, -0.2, True) # (tripod top)
    x,y,z = calculate_pos(640.0, 400.0, 318, 307, 400.0, d2) #
    p2 = [x,y,z]

    print ''
    d3 = calculate_distance(640.0, 400.0, 474, 459, 80.0, 400.0, -0.2) # (door handle)
    x,y,z = calculate_pos(640.0, 400.0, 474, 305, 400.0, d3) #
    p3 =[x,y,z]
    
    print ''
    im_p1g = Image.new('F', (640,400))
    im_p2g = Image.new('F', (640,400))
    p1g = im_p1g.load()
    p2g = im_p2g.load()
    for j in range(640):
        for k in range(400):
            p1g[j,k] = rgb2gray(*pix1[j, k])
            p2g[j,k] = rgb2gray(*pix2[j, k])
    p1g = normalize_im(p1g, 640, 400)
    p2g = normalize_im(p2g, 640, 400)
    x,y,val = calculate_match(p1g, p2g,267, 264, -4)
    x,y,val = calculate_match(p1g, p2g,318, 307, -4)
    x,y,val = calculate_match(p1g, p2g,474, 305, -4)
    x,y,val = calculate_match(p1g, p2g,470, 154, -4, verbose=True)
    x,y,val = calculate_match(p1g, p2g,319, 97, -4, verbose=True)
    if False:
        im3 = Image.new('RGB', (11, 11))
        im4 = Image.new('RGB', (11, 11))
        #im3 = Image.new('F', (11, 11))
        #im4 = Image.new('F', (11, 11))
        ld3 = im3.load()
        ld4 = im4.load()
        for i in range(11):
            for j in range(11):
                ld3[i,j] = pix1[267-5+i, 264-5+j]
                ld4[i,j] = pix2[240-5+i, 260-5+j]
                #ld3[i,j] = rgb2gray(*pix1[267-5+i, 264-5+j])
                #ld4[i,j] = rgb2gray(*pix2[240-5+i, 259-5+j])
        fig = pylab.figure()
        pylab.imshow(im3)
        fig = pylab.figure()
        pylab.imshow(im4)
        pylab.show()
    return
    
    ps = [p1,p2,p3]
    print ps

    match = True
    if match:
        res = match_lr(e_im1, p1g, p2g, 640, 400, -4, 10)
        res.sort(key=lambda x:x[4]) #get some threshold
    if False: #matplit 3D -- too slow
        for x1,y1,x2,y2,val in res[:10000]:
            if x1==x2: continue
            d = calculate_distance(640.0, 400.0, x1, x2, 80.0, 400.0, -0.2)
            x,y,z = calculate_pos(640.0, 400.0, x1, y1, 400.0, d)
            ps.append([x,y,z])

        draw2(ps)
        plt.show()
    if False: #display original edge only
        imd = Image.new('RGB', (640, 400))
        ld = imd.load()
        for i in range(400):
            for j in range(640):
                if e_im1[i][j] != 0:
                    ld[j, i] = (200,200,200)
        fig = pylab.figure()
        pylab.imshow(imd)
        pylab.show()

    if True:
        imd = Image.new('RGB', (640, 400))
        ld = imd.load()

        for x1,y1,x2,y2,val in res[:10000]:
            if x1==x2: continue
            d = calculate_distance(640.0, 400.0, x1, x2, 80.0, 400.0, -0.2)
            r, g, b = pixel(d, width=3000, map=heatmap)
            r, g, b = [int(256*v) for v in (r, g, b)]
            #r = int(gaussian(x, 158.8242, 201, 87.0739) + gaussian(x, 158.8242, 402, 87.0739))
            #g = int(gaussian(x, 129.9851, 157.7571, 108.0298) + gaussian(x, 200.6831, 399.4535, 143.6828))
            #b = int(gaussian(x, 231.3135, 206.4774, 201.5447) + gaussian(x, 17.1017, 395.8819, 39.3148))
            ld[x1, y1] = (r, g, b)
        fig = pylab.figure()
        pylab.imshow(imd)
        pylab.show()
        return
    
    return

    '''
    print pix1[1150,305]
    pix1[1495,560]=(255,0,0)
    pix2[1500,560]=(255,0,0)
    pix1[1164,307]=(255,255,255)
    pix2[1150,305]=(255,255,255)
    '''
    if show:
        fig = pylab.figure()
        pylab.imshow(im_p1g) #pylab.imshow(im1)
        fig = pylab.figure()
        pylab.imshow(im_p2g)
        pylab.show()
    return pix1, pix2
 
def use_pil():
    imageio.imwrite('/tmp/a.png', image)
    im = Image.open('/tmp/a.png') #Can be many different formats.
    pix = im.load()
    x,y=200,200
    print im.size #Get the width and hight of the image for iterating over
    print pix[x,y] #Get the RGBA Value of the a pixel of an image

def main():
    #return gradient_color_demo()
    return image_read(True)

    pix1, pix2 = image_read()
    cal_pos(pix1, pix2)
    point_pos(pix1,pix2)

if __name__=='__main__':
    main()
    
'''
Calibration:
1. get l/r pics, ruler measure the len_distance
2. mark a point on l/r, ruler get its distance, get its pic coordinations as x1, x2 (assume y1~=y2)
3. calculate focus length, x_off_center
4. verify the focus_lenght with another 2 points( as step2), at different Z and X

Point of cloud, 1 frame:
1. get FAST/custom matching points(Ps), left len as xyz_Zero
2. for each p in Ps: z=distance, x=(x1-center)*z/f
3. Other p in pics?

static lens:
moving Ps in an environment

moving lens:
stitch 3D environments to A relative environment
moving Ps in the new environment

Object guess:
Query moving Ps against 3D-Obj-Libs
Or
project moving Ps to 2D, query against 2D libs.
'''
