import sys, math
import time
import numpy as np
import heapq
import pylab
import imageio #read video
from PIL import Image, ImageEnhance
import cv2
import rasl #image alignment
from scipy import misc

import p3match
#rebuild p3match:  pip install Cython
#cypthon p3match.pyx;
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o p3match.so p3match.c

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

heatmap = [
    [0.0, (1, 0, 0)],
    [0.20, (0.8, 0, 0)],
    [0.40, (0.6, 0.5, 0)],
    [0.60, (.4, 0.6, 0.4)],
    [0.80, (0, .75, 0.6)],
    [0.90, (0, 0, 0.8)],
    [1.00, (0, 0, 1.0)],
]

#revese heatmap
#heatmap = heatmap[1:3]
#heatmap = heatmap[::-1]

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

def get_edges(img_file, sigma, t, T):
    img = to_ndarray(img_file)
    img = gs_filter(img, sigma)
    img, D = gradient_intensity(img)
    img = suppression(img, D)
    img, weak = threshold(img, t, T)
    img = tracking(img, weak)
    return img

def normalize_im(px, w, h):
    mn1, mx2=255,0
    for i in range(w):
        for j in range(h):
            mx2 = max(mx2, px[i,j])
            mn1 = min(mn1, px[i,j])
    for i in range(w):
        for j in range(h):
            #px[i,j] = int( (px[i,j]-mn1+0.001)/(mx2-mn1+0.001)*255.0 )
            px[i,j] = int( (px[i,j]-mn1) )
    return px

#match whole line (x1_i,y1) -> (x2, y2), some of the (x1_i, y1) maybe hidden (on left half) 
#match block x1,y1, iw, ih(block) to right
def calculate_match_block(px1, px2, ix1, y1, y_offset, iw=40, ih=20, max_right=100, verbose=False): 
    w,h=640,400
    # right start from x1, y2
    y2 = y1+y_offset
    res = []
    for x2 in range(ix1, ix1-100, -1): #im_left to right
        val = 0
        #calulate max min
        mn1,mx1,mn2,mx2=255,0,255,0
        normal = False
        for i in range(iw):
            break
            for j in range(ih):
                a, b= px1[ix1+i,y1+j], px2[x2+i, y2+j]
                if mn1 > a: mn1=a
                if mn2 > b: mn2=b
                if mx1 < a: mx1=a
                if mx2 < b: mx2=b
        if mx1-mn1 < 8:# and mx2-mn2<5 and abs(mn1-mn2)<6:
            normal = True
            #return ix1, 0
        for i in range(iw):
            for j in range(ih):
                d = abs(px1[ix1+i,y1+j] - px2[x2+i, y2+j])
                val +=  d*d
        res.append([x2,round(val, 2)])
    res = heapq.nsmallest(5, res, key=lambda x:x[1])
    x2,val = res[0]
    _, val1 = res[1]
    _,val2 = res[4]
    de = (val2-val)/val

    if verbose:
        d = calculate_distance(640.0, 400.0, ix1, x2, 80.0, 400.0, -0.2)
        print 'block ({0},{3}) {1}: distance {2}mm, tangle-{4:.2f}'.format(ix1, x2, int(d), y1, d/(ix1-321))
        print res[:5]
    if abs(ix1-100)<5 and abs(y1-100) < 5:
       print "debug", val, ix1, y1, de
    if abs(ix1-320)<5 and abs(y1-80) < 5:
       print "debug", val, ix1, y1, de
    #if (val2-val)/val < 0.08 or val < 9000: #significant difference threshold
    if iw==40:
        if (val2-val)/val < 0.08 or val < 8000: #significant difference threshold
            return ix1, 0
    if iw==20:
        pass
    return x2,val

def pre_process(px, sigma=1.4): #blur filter
    img = px.astype('int32')
    img = gs_filter(img, sigma)
    #img, D = gradient_intensity(img)
    #img = suppression(img, D)
    return img

#find a formula that makes a1-a2 < a1-a3; fix gray/white match
def test_adiff(a1, a2, a3):
    print 'test array diff'
    z= (20, 20)
    a1 = normalize_im(a1, 20, 20)
    a2 = normalize_im(a2, 20, 20)
    a3 = normalize_im(a3, 20, 20)
    print 'A1: ', a1
    print 'A2: ', a2
    print 'A3: ', a3
    def adiff(a,b):
        v = 0
        for i in range(20):
            for j in range(20):
                d = abs(a[i,j] - b[i,j])
                v += d*d
        return v
    print adiff(a1,a2), adiff(a1,a3) , adiff(a2,a3), adiff(a1,a1)
#sharp then 50X50 sub-block coarse match starting from 20X20
def image_read(show=False, block=False):  
    im1 = Image.open('/tmp/a.jpg') #left
    im2 = Image.open('/tmp/b.jpg') #right
    
    if False:
        im1 = ImageEnhance.Contrast(im1) #sharp filter/blur filter: no difference
        im2 = ImageEnhance.Contrast(im2)
        pix1, pix2 = im1.enhance(2).load(), im2.enhance(2).load()
    else:
        pix1, pix2 = im1.load(), im2.load()

    im3 = Image.new('F', (640,400))
    im4 = Image.new('F', (640,400))
    p11 = im3.load()
    p22 = im4.load()
    
    for i in range(640):
        for j in range(400):
            p11[i,j] = rgb2gray(*pix1[i,j])
            p22[i,j] = rgb2gray(*pix2[i,j])

    #p11 = normalize_im(p11, 640, 400)
    #p22 = normalize_im(p22, 640, 400)

    a1 = np.zeros([20, 20], dtype = np.intc)
    a2 = np.zeros([20, 20], dtype = np.intc)
    a3 = np.zeros([20, 20], dtype = np.intc)
    x1,y1,y2 = 100,100, 96
    for i in range(20):
        for j in range(20):
            a1[i,j] = p11[x1+i, y1+j]
            a2[i,j] = p22[92+i, y2+j]
            a3[i,j] = p22[86+i, y2+j]
    #test_adiff(a1, a2, a3)
    #return

    x2, val = calculate_match_block(p11, p22, 260, 260, -4, verbose=True) #bed pole top, 1
    x2, val = calculate_match_block(p11, p22, 300, 300, -4, verbose=True) #projector left top, 2
    x2, val = calculate_match_block(p11, p22, 320, 300, -4, verbose=True) #projector right top, 3

    #because the len is not diagonal to wall
    x2, val = calculate_match_block(p11, p22, 300, 80, -4, verbose=True) #top ceiling edge, middle, too short, 4? 
    x2, val = calculate_match_block(p11, p22, 300, 90, -4, verbose=True) #top ceiling edge, 5
    x2, val = calculate_match_block(p11, p22, 100, 100, -4, verbose=True) #top ceiling edge, left, too far, 6
    x2, val = calculate_match_block(p11, p22, 480, 100, -4, verbose=True) #lef upper vent, 7: correct

    #Special case 1: #white space, either ZERO shift or below actural value
    x2, val = calculate_match_block(p11, p22, 400, 200, -4, verbose=True) #wall on right side of door knob
    # x2==x1: derive from adjacent block
    
    #Special case 2: similar to special case 1, x2 ~= x1
    # because gray is 140 vs 157 in case No. 6, 5, 4

    #special case 3:
    x2, val = calculate_match_block(p11, p22, 440, 80, -4, verbose=True) #top ceiling right, too close, why?
    x2, val = calculate_match_block(p11, p22, 480, 80, -4, verbose=True) #top ceiling right, too close, why?
    x2, val = calculate_match_block(p11, p22, 320, 80, -4, verbose=True) #top ceiling right, too close, why?

    x2, val = calculate_match_block(p11, p22, 480, 300, -4, verbose=True) #near door knob
    x2, val = calculate_match_block(p11, p22, 460, 300, -4, verbose=True) 
    x2, val = calculate_match_block(p11, p22, 480, 320, -4, verbose=True) 
    x2, val = calculate_match_block(p11, p22, 480, 280, -4, verbose=True) 
    
    
     #color grey: left x1~x2, right x3~x4, x1-x2=( x1-x3, x2-x4)
    x2, val = calculate_match_block(p11, p22, 480, 344, -4, verbose=True)
    x2, val = calculate_match_block(p11, p22, 520, 84, -4, verbose=True)

    #down right (door left bottom)
    x2, val = calculate_match_block(p11, p22, 520, 364, -4, verbose=True)
    
    x2, val = calculate_match_block(p11, p22, 280, 324, -4, verbose=True)
    #return
    
    if block: #match all
        out = np.zeros([640, 400], dtype = np.intc)
        imd = Image.new('RGB', (640, 400))
        ld = imd.load()
        match_start = time.time()
        iw,ih = 40,20
        for y1 in range(4, 380, 20):
          for x1 in range(100, 600, 40):
            x2, val = calculate_match_block(p11, p22, x1, y1, -4)
            d = calculate_distance(640.0, 400.0, x1, x2, 80.0, 400.0, -0.2)
            if d > 1500:
                for i in range(iw):
                  for j in range(ih):
                    out[x1+i,y1+j] = d
            else: #look close object
              for k in range(0, 40, 20):
                x2, val = calculate_match_block(p11, p22, x1+k, y1, -4, iw=20, ih=20)
                d = calculate_distance(640.0, 400.0, x1+k, x2, 80.0, 400.0, -0.2)
                for i in range(20):
                  for j in range(ih):
                    out[x1+k+i,y1+j] = d
            
        match_dur = time.time() - match_start
        print "match time ", "{0:.2f}".format(match_dur)
        
        for y1 in range(4, 380, 20):
          for x1 in range(100, 600, 20):
            d = out[x1,y1]
            if d==0: continue
            r, g, b = pixel(d, width=4500, map=heatmap)
            r, g, b = [int(256*v) for v in (r, g, b)]
            for i in range(iw):
              for j in range(ih):
                ld[x1+i, y1+j] = (r, g, b)
        fig = pylab.figure()
        pylab.imshow(imd)
        pylab.show()
        return
        
def main():
    #return gradient_color_demo()
    if len(sys.argv)>1:
        print sys.argv
        if sys.argv[1]=='test':
            return show_test()
    return image_read(show=True, block=True)

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
