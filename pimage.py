import sys, math
import pylab
import imageio #read video
from PIL import Image #read image
#import rasl #image alignment

len_d = 60.0 #mm, Panasonic AG-3DA1 HD 3D camera
focus = 15.0 #mm
pixel_d = 10
center_offset = 5
def cal_pos(pix1, pix2):
    #maunal calibration, (x,y):Horizon-Y, vertic X
    # L(362,912), R(362,920)
    # L(560, 1495), R(560, 1500)
    # L(305, 1150), R(306,1160)
    w, h = 1920.0, 1080.0
    cps = [ [(362,912), (362,920)], [(560, 1495), (560, 1500)], [(307, 1164), (305,1150)]]
    for items in cps:
        for j in items:
            j = (j[1], j[0])

    #can be derived by openCV edge detection/SURF features
    print ('Calibration')
    for ps in cps:
        print (ps)
        p1,p2 = ps
        y1, x1 = p1
        y2, x2 = p2
        
        #image may not at the lens center, center_offset
        # "5" need calibration each run (vibration)
        x1 = abs(x1 - w/2 + 5) 
        x2 = abs(x2 - w/2 - 5)
        if x2>x1: #swap, side same, not in the middle
            x1,x2=x2,x1
        
        #pixel_d is calibrate once only( because f is not consistent with real camera)
        d = len_d*focus*pixel_d/(x1-x2)
        print ("{0:.2f}m {1} {2} {3}".format(d/100, x1, x2, (x2-x1)))

        #calculate x,y (z=d)

def alignment(pix1, pix2):
    print ('align...')

#given pixel_d, center_offset from above calibration
def point_pos(pix1, pix2):
    print ('\ncalculate points\' x,y,z')

def image_read(show=False):
    im1 = Image.open('/tmp/a.png') #left
    im2 = Image.open('/tmp/b.png') #left
    pix1, pix2 = im1.load(), im2.load()

    #test calibration point (X/Y revert with imageio), horizion-X
#    print pix1[1150,305]
    pix1[912,362]=(0,255,0)
    pix2[920,362]=(0,255,0)
    pix1[1495,560]=(255,0,0)
    pix2[1500,560]=(255,0,0)
    pix1[1164,307]=(255,255,255)
    pix2[1150,305]=(255,255,255)

    if show:
        fig = pylab.figure()
        pylab.imshow(im1)
        fig = pylab.figure()
        pylab.imshow(im2)
        pylab.show()
    return pix1, pix2
    
def test_read():
    filename = sys.argv[1] #3D_33_LEFT.mp4 right
    vid = imageio.get_reader(filename,  'ffmpeg')
    print (vid.get_meta_data())
    nums = [10, 287]
    for num in nums:
        timestamp = float(num)/ vid.get_meta_data()['fps']
        print (timestamp)
        image = vid.get_data(num)
        image = imageio.core.image_as_uint(image)
        fig = pylab.figure()
        fig.suptitle('image #{}'.format(num), fontsize=20)
        pylab.imshow(image)
#        print [i[200:202] for i in image[200:202]]
#        print len(image), len(image[0]), image[305][1149:1152]
#        print image.shape, image.size, image.meta
        imageio.imwrite(sys.argv[2], image)
        break
    #pylab.show()

def use_pil():
    imageio.imwrite('/tmp/a.png', image)
    im = Image.open('/tmp/a.png') #Can be many different formats.
    pix = im.load()
    x,y=200,200
#    print im.size #Get the width and hight of the image for iterating over
#    print pix[x,y] #Get the RGBA Value of the a pixel of an image

def opencv_dp():
    import numpy as np
    import cv2
    from matplotlib import pyplot as plt

    imgL = cv2.imread('/tmp/a.png',0)
    imgR = cv2.imread('/tmp/b.png',0)

    #stereo = cv2.createStereoBM(numDisparities=16, blockSize=15)
    stereo = cv2.StereoBM(ndisparities=16, SADWindowSize=15)
#    print (stereo)
    disparity = stereo.compute(imgL,imgR)
    plt.imshow(disparity,'gray')
    plt.show()

def main():
    #test_read()
    #return opencv_dp()
    return image_read(True)

    pix1, pix2 = image_read()
    cal_pos(pix1, pix2)
    point_pos(pix1,pix2)

if __name__=='__main__':
    main()
