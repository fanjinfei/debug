import sys, math
import pylab
import imageio #read video
from PIL import Image #read image
import rasl #image alignment

len_d = 60.0 #mm, PS4 eye
focus = 15.0 #mm
center_offset = 5
#^panasonic 3D parameter

#PS4 eye parameter: len_d=80.0mm focus=4.0mm
len_d=80.0
pixel_ratio=100.0 #each pix distance?
focus=4.0*100 #100: pixel->ratio
center_offset = -0.2

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

def image_read(show=False):
    im1 = Image.open('/tmp/a.jpg') #left
    im2 = Image.open('/tmp/b.jpg') #left
    pix1, pix2 = im1.load(), im2.load()

    #test calibration point (X/Y revert with imageio), horizion-X
    pix1[267,264]=(0,255,0)
    pix2[240,260]=(0,255,0)
    #fl = calculate_focus(640.0, 400.0, 267, 240, 80.0, 1200.0) #manual measure distance 120.0CM, len_d=8.0CM
    calculate_distance(640.0, 400.0, 267, 240, 80.0, 400.0, -0.2) # (bed pole)
    calculate_pos(640.0, 400.0, 267, 264, 400.0, 1203.0) #
    
    print ''
    d2 = calculate_distance(640.0, 400.0, 318, 305, 80.0, 400.0, -0.2) # (tripod top)
    calculate_pos(640.0, 400.0, 318, 307, 400.0, d2) #

    print ''
    d3 = calculate_distance(640.0, 400.0, 474, 459, 80.0, 400.0, -0.2) # (door handle)
    calculate_pos(640.0, 400.0, 474, 305, 400.0, d3) #
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

Point of cloud:
1. get FAST matching points(Ps), left len as xyz_Zero
2. for each p in Ps: z=distance, x=(x1-center)*z/f
3. Other p in pics?
'''
