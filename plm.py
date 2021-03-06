import sys, math
import time,json
import numpy as np
import heapq
from PIL import Image, ImageFilter #Pillow
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
#from line2d import line2d
from mpl_toolkits.mplot3d import Axes3D
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
    print ("focus lenght {0:.2f}mm, {1} {2} {3}".format(focus, x1, x2, (x1-x2)))
    return focus
    
def calculate_distance(w, h, x1, x2, len_d, focus, x_off_center, verbose=False): #from manually marked points to distance
    x1 = (x1 - w/2 +x_off_center ) #left
    x2 = (x2 - w/2 -x_off_center ) #right
    delta = abs(x1-x2)
    d = len_d*focus/delta
    if verbose:
        print ("distance lenght {0:.2f}mm, {1} {2} {3}".format(d, x1, x2, delta) )
    return d

def calculate_pos(w, h, x1, y1, focus, z, verbose=False): #from 
    x = z/focus*(x1-w/2 +center_offset)
    y = z/focus*(y1-h/2)
    if verbose:
        print ("pos xyz {0:.2f}mm, {1:.2f} {2:.2f}".format(x, y, z))
    return x,y,z

def image_read(show=False):
    im1 = Image.open('/tmp/a.jpg') #left
    im2 = Image.open('/tmp/b.jpg') #left
    
    #display in two windows
    #im1.show()
    #im2.show()
    
    pix1, pix2 = im1.load(), im2.load()

    #test calibration point (X/Y revert with imageio), horizion-X
    # left image Y axis is 4 more than right
    #pix1[267,264]=(0,255,0) #marker green  TWO dimension array is pixel
    #pix2[240,260]=(0,255, 0) #marker blue
    print(pix1[266,264]) # (253, 230, 199)

    fl = calculate_focus(640.0, 400.0, 267, 240, 80.0, 1200.0) #manual measure distance 120.0CM, len_d=8.0CM
    print("focus is ", fl)
    
    z = calculate_distance(640.0, 400.0, 267, 240, 80.0, 400.0, -0.2, verbose=True) # (bed pole)
    x,y,z = calculate_pos(640.0, 400.0, 267, 264, 400.0, 1203.0, ) #
    p1 = (x,y,z)
    print (p1)
    #import pdb; pdb.set_trace()
    a = [ pix1[x, 264] for x in range(0,640)]
    b = [ pix2[x, 260] for x in range(0,640)]
    

    c = [ pix1[x, 279] for x in range(0,640)]
    d = [ pix2[x, 275] for x in range(0,640)]

    e = [ pix1[x, 314] for x in range(0,640)]
    f = [ pix2[x, 310] for x in range(0,640)]
    return a,b, c,d, e,f

def main():
    a,b, c,d, e,f = image_read(True)
    with open('/tmp/lr.json', 'w') as outfile:
        json.dump([a,b,c,d, e,f], outfile)
    #line2d(a,b)
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
