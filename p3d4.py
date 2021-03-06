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

import blreg #block register (depth+2d)
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
    [0.20, (0.8, 0.2, 0.2)],
    [0.40, (0.6, 0.5, 0.3)],
    [0.60, (.4, 0.6, 0.4)],
    [0.80, (0.2, .75, 0.6)],
    [0.90, (0.1, 0.8, 0.8)],
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
#return val=0: too plain, ignore whole block
#       val=-1: too much infor, goto sub-block
def calculate_match_block(data, ix1, y1, y_offset, iw=40, ih=20, max_right=100, verbose=False): 
    px1, px2 = data['p11'], data['p22']
    em1, em2 = data['em1'], data['em2'] #skip the non edge part
    
    w,h=640,400
    # right start from x1, y2
    y2 = y1+y_offset
    res = []
    es = 0
    for i in range(iw):#get edge points (set a minimum 5)
        for j in range(ih):
            es += em1[y1+j, ix1+i]
    if es < 5 : return ix1,0 #no significant pixels

    for x2 in range(ix1, ix1-100, -1): #im_left to right
        val = 0
        es = 0
        for i in range(iw):#get edge points (set a minimum 5)
            for j in range(ih):
                es += em2[y2+j, x2+i]
        if es < 5 : continue #no significant pixels
        for i in range(iw):
            for j in range(ih):
                d = abs(px1[ix1+i,y1+j] - px2[x2+i, y2+j])
                val +=  d*d
        res.append([x2,round(val, 2)])
    if not res: return ix1, 0
    res = heapq.nsmallest(5, res, key=lambda x:x[1])
    x2,val = res[0]
    _, val1 = res[1]
    _,val2 = res[4]
    de = (val2-val)/val

    if verbose:
        d = calculate_distance(640.0, 400.0, ix1, x2, 80.0, 400.0, -0.2)
        print 'block ({0},{3}) {1}: distance {2}mm, tangle-{4:.2f}'.format(ix1, x2, int(d), y1, d/(ix1-321))
        print iw, ih, res[:5]
    if abs(ix1-100)<5 and abs(y1-100) < 5:
       print "debug", val, ix1, y1, de
    if abs(ix1-320)<5 and abs(y1-80) < 5:
       print "debug", val, ix1, y1, de
    
    #if ix1-x2 < 2: return ix1,0 #too close
    if iw==40:
        if val > 250000: return x2, -1 #sub
        #if (val2-val)/val < 0.1 or val < 9000 or val2 < 15000 : #significant difference threshold
        #    return ix1, 0
    if iw==20:
        if val > 400000: return x2,-1 #sub-block
        #if (val2-val)/val < 0.1 or val < 4000:
        #    return ix1, 0
    if iw==10 and ih==10:
        if val > 100000: return x2, -1 #consider as occulsion; if not to divide any more
        #if (val2-val)/val < 0.2 or val < 500: #plain white color
        #    return ix1, 0
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
    
def fill_hgap(out, y1, bs, iw=10, ih=10):
    return
    x1,d1 = bs[0]
    x2,d2 = bs[-1]
    dx = max(d1,d2)
    if d1 ==0 or d2==0: #should look up/down
        return
    for x,d in bs[1:-1]: #middle-> left/right ?
        for i in range(iw):
            for j in range(ih):
                out[x+i,y1+j] = dx
    
#sharp then 50X50 sub-block coarse match starting from 20X20
def image_read(fn_l, fn_r, show=False):
    im1 = Image.open(fn_l) #left
    im2 = Image.open(fn_r) #right
    e_im1 = get_edges(fn_l, 1.4, 20, 40) #left
    e_im2 = get_edges(fn_r, 1.4, 20, 40) #left
    
    pix1, pix2 = im1.load(), im2.load()

    p11 = np.zeros((640,400))
    p22 = np.zeros((640,400))
    
    for i in range(640):
        for j in range(400):
            p11[i,j] = rgb2gray(*pix1[i,j])
            p22[i,j] = rgb2gray(*pix2[i,j])

    data ={}
    data['p11'] = p11
    data['p22'] = p22
    data['em1'] = e_im1
    data['em2'] = e_im2
    
    out = np.zeros([640, 400], dtype = np.intc)
    imd = Image.new('RGB', (640, 400))
    ld = imd.load()
    match_start = time.time()

    iw,ih = 40,20
    for y1 in range(4, 380, 20):
      for x1 in range(100, 600, 40): #40X20
        x2, val = calculate_match_block(data, x1, y1, -4)
        d = calculate_distance(640.0, 400.0, x1, x2, 80.0, 400.0, -0.2)
        if val==0: continue
        if val!=-1:
            for i in range(iw):
              for j in range(ih):
                out[x1+i,y1+j] = d
        else: #look close object
          for k in range(0, 40, 20): #20X20
            x2, val = calculate_match_block(data, x1+k, y1, -4, iw=20, ih=20)
            #if val > xxxx: It is occlusion; or need to divide to small block
            d = calculate_distance(640.0, 400.0, x1+k, x2, 80.0, 400.0, -0.2)

            if val==0: continue
            if val!=-1:
              for i in range(20):
                for j in range(ih):
                  out[x1+k+i,y1+j] = d
            else: #use 10X10 block
                for l in range(0,20,10):
                    for m in range(0,20,10):
                        x2, val = calculate_match_block(data, x1+k+l, y1+m, -4, iw=10, ih=10)
                        d = calculate_distance(640.0, 400.0, x1+k+l, x2, 80.0, 400.0, -0.2)

                        if val ==-1 or val==0: #occlusion or white
                            continue
                        for i in range(10):
                          for j in range(10):
                            out[x1+k+l+i,y1+m+j] = d
            
        match_dur = time.time() - match_start
        print "match time ", "{0:.2f}".format(match_dur)
        
        for y1 in range(4, 380, 10):
          left,right=0,0
          bs = []
          for x1 in range(100, 600, 10): #scan the empty block
              d = out[x1,y1]
              if out[x1,y1]!=0: #head or tail; or continous
                  if bs:
                      if len(bs)>1: #end of the empty gap
                          bs.append([x1,d])
                          #fix gap
                          fill_hgap(out, y1, bs)
                          bs = []
                          bs.append([x1,d])
                      elif len(bs) == 1: #head
                          if bs[-1][1] != 0:
                              bs[0] = [x1,d]
                          else:
                              bs.append([x1,d])
                              #fix gap
                              fill_hgap(out, y1, bs)
                              bs=[]
                              bs.append([x1,d])
                  else: bs.append([x1,d]) #head
              else: #gap
                  bs.append([x1,d])
          if bs: 
            if bs[0][0] == 0: #whole line is empty
                pass #TODO: look up and down neighbors
            else: # right part
                #fix right gap
                pass

        for y1 in range(4, 380, 10):
          for x1 in range(100, 600, 10):
            d = out[x1,y1]
            if d==0: continue
            r, g, b = pixel(d, width=4500, map=heatmap)
            r, g, b = [int(256*v) for v in (r, g, b)]
            for i in range(10):
              for j in range(10):
                ld[x1+i, y1+j] = (r, g, b)
        if show:
            fig = pylab.figure()
            pylab.imshow(imd)
            pylab.show()
        return out, p11

#time sequence: 1, 2
# case 1: viewer position static, with/without moving object (1.1, 1.2)
# case 2: viewer moving, with/without moving object (2.1 2.2)
def seq_match(seq1, seq2): #15 FPS
    f1 = '/tmp/{0}_l.jpg'.format(seq1)
    f2 = '/tmp/{0}_r.jpg'.format(seq1)
    f3 = '/tmp/{0}_l.jpg'.format(seq2)
    f4 = '/tmp/{0}_r.jpg'.format(seq2)

    #get matched block, with estimated empty(white/occlusion, ignore it for now)
    bl1, pix1 = image_read(f2, f1)
    bl2, pix2 = image_read(f4, f3)

    data = {}
    data['bl1'] = bl1
    data['bl2'] = bl2
    data['px1'] = pix1
    data['px2'] = pix2
    #10X10 blocks (maybe more small?)
    
    if True:
        blreg.imreg(data, 320, 334)
        return 
    res= []
    for y1 in range(4, 380, 10):
      for x1 in range(100, 600, 10):
        x2,y2, val, d = blreg.imreg(data, x1, y1)
        res.append([x2,y2,val, d])
    res.sort(key = lambda k: -k[2])
    
    print res[:5]

def flip_img(src, fn):
    imd = Image.new('RGB', (640, 400))
    ld = imd.load()
    for i in range(400):
         for j in range(640):
             r,g,b = src[i][639-j]
             ld[j,i] = (r,g,b)
    imd.save(fn, "JPEG", quality=100, optimize=False, progressive=False)

def test_read( filename):
    #filename = sys.argv[1] #3D_33_LEFT.mp4 right
    vid = imageio.get_reader(filename,  'ffmpeg')
    print vid.get_meta_data()
    nums = [2, 3]
    for num in nums:
        timestamp = float(num)/ vid.get_meta_data()['fps']
        print timestamp
        image = vid.get_data(num)
        image = imageio.core.image_as_uint(image)
        fig = pylab.figure()
        fig.suptitle('image #{}'.format(num), fontsize=20)
        pylab.imshow(image)
        print len(image), len(image[0]), image[100][100]
        print image.shape, image.size, image.meta
        img_name='/tmp/{0}_{1}.jpg'.format(num, filename[-5])
        #imageio.imwrite(img_name, image)
        flip_img(image, img_name)
#        break
    #pylab.show()

def show_image(f1, f2):
    im1 = Image.open(f1) #left
    im2 = Image.open(f2) #left
    pix1, pix2 = im1.load(), im2.load()

    fig = pylab.figure()
    pylab.imshow(im1)
    fig = pylab.figure()
    pylab.imshow(im2)
    pylab.show()
        
def main():
    #return gradient_color_demo()
    if len(sys.argv)>1:
        print sys.argv
        if sys.argv[1]=='test':
            return show_image(sys.argv[2], sys.argv[3])
        if sys.argv[1][-4:]=='.mp4':
            return test_read(sys.argv[1])
        if sys.argv[1] =='depth': #depth detection of 2 jpg
            return image_read(sys.argv[2], sys.argv[3], show=True, block=True)

    return seq_match(sys.argv[1], sys.argv[2])

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
