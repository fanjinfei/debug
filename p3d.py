import sys, math
import numpy as np
import pylab
import imageio #read video
from PIL import Image #read image
import rasl #image alignment

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
heatmap = heatmap[:-3]

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def pixel(x, width=100, map=[], spread=1):
    width = float(width)
    r = sum([gaussian(x, p[1][0], p[0] * width, width/(spread*len(map))) for p in map])
    g = sum([gaussian(x, p[1][1], p[0] * width, width/(spread*len(map))) for p in map])
    b = sum([gaussian(x, p[1][2], p[0] * width, width/(spread*len(map))) for p in map])
    return min(1.0, r), min(1.0, g), min(1.0, b)

def gradient_color_demo():
    import math
    from PIL import Image
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
    
def calculate_distance(w, h, x1, x2, len_d, focus, x_off_center): #from manually marked points to distance
    x1 = abs(x1 - w/2 +x_off_center ) #left
    x2 = abs(x2 - w/2 -x_off_center ) #right
    delta = abs(x1-x2)
    d = len_d*focus/delta
    print "distance lenght {0:.2f}mm, {1} {2} {3}".format(d, x1, x2, delta)
    return d

def calculate_pos(w, h, x1, y1, focus, z): #from 
    x = z/focus*(x1-w/2 +center_offset)
    y = z/focus*(y1-h/2)
    print "pos xyz {0:.2f}mm, {1:.2f} {2:.2f}".format(x, y, z)
    return x,y,z

def calulate_diff(pix1, pix2): #10X10 square
    return 0

#input: left/right image, left p1(x1,y1), y_offset + y1 = y2
#output:match p2(x2,y2), val(confidence)
def calculate_match(px1, px2, x1, y1, y_offset): 
    x2, y2 = x1, y1
    val = 0.0
    threshold = 0.0 #mininum matching
    return x2,y2,val

#ouput 3D PC, zero in left lens
def match_lr(px1, px2):
    #match each of the p1 in px1 to p2 in px2, sort them in order
    ms = []
    return None

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

def image_read(show=False):
    im1 = Image.open('/tmp/a.jpg') #left
    im2 = Image.open('/tmp/b.jpg') #left
    pix1, pix2 = im1.load(), im2.load()

    #test calibration point (X/Y revert with imageio), horizion-X
    pix1[267,264]=(0,255,0)
    pix2[240,260]=(0,255,0)
    #fl = calculate_focus(640.0, 400.0, 267, 240, 80.0, 1200.0) #manual measure distance 120.0CM, len_d=8.0CM
    calculate_distance(640.0, 400.0, 267, 240, 80.0, 400.0, -0.2) # (bed pole)
    x,y,z = calculate_pos(640.0, 400.0, 267, 264, 400.0, 1203.0) #
    p1 = [x,y,z]
    
    print ''
    d2 = calculate_distance(640.0, 400.0, 318, 305, 80.0, 400.0, -0.2) # (tripod top)
    x,y,z = calculate_pos(640.0, 400.0, 318, 307, 400.0, d2) #
    p2 = [x,y,z]

    print ''
    d3 = calculate_distance(640.0, 400.0, 474, 459, 80.0, 400.0, -0.2) # (door handle)
    x,y,z = calculate_pos(640.0, 400.0, 474, 305, 400.0, d3) #
    p3 =[x,y,z]
    
    print ''
    x,y,val = calculate_match(pix1, pix2,267, 264, -4) 
    
    ps = [p1,p2,p3]
    print ps
    draw2(ps)
    if True:
      plt.show()
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
        pylab.imshow(im1)
        fig = pylab.figure()
        pylab.imshow(im2)
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
