import json
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

__display = False

def rgb255_to_clab(a):
    color1_rgb = sRGBColor(a[0]/255.0, a[1]/255.0, a[2]/255.0);
    color1_lab = convert_color(color1_rgb, LabColor);
    return color1_lab

def read():
    with open('/tmp/lr.json') as json_file:
        data = json.load(json_file)
        return data

def calculate_d( x1, x2, len_d=80, focus=400, x_off_center=-0.2,w=640, h=480, verbose=False): #from manually marked points to distance
    x1 = (x1 - w/2 +x_off_center ) #left
    x2 = (x2 - w/2 -x_off_center ) #right
    delta = abs(x1-x2)
    d = len_d*focus/delta
    if verbose:
        print ("distance lenght {0:.2f}mm, {1} {2} {3}".format(d, x1, x2, delta) )
    return d
    
# given: matched (x1_r, x1_l) of z1, matched(x2_r, x2_l) of z2
# if (x1_r-x2_r) != (x1_l - x2_l) : delta is the occlusion
# make sure z1 (l/r) is both matched (otherwise lost perception here), then x2 is occluded.
def calulate_occlusion(x1_l, x1_r, x2_l, x2_r, z1, z2, len_d=80, focusn=400): #for re-affirm with length
    #(x1_l, x2_l).z1 => (x2_r, x2_r)(xx ..) are occluded at z2
    #assume x1<x2 and x2_l-x1_l > x2_r-x1_r ?
    delta = (x2_l-x1_l) - (x2_r - x1_r)
    x3 = x2_l - delta
    z2_n = len_d*focusn/abs(delta)
    return z2_n #other side's depth of x2
    
def rgb2gray(R,G,B):
    return 0.21*R + 0.72*G + 0.07*B
    
def match(d1, y1): #d1: right side's first half, y1: full left side
    from scipy.fftpack import fft
    N=320
    y = fft(d1)
    return
    
def match_gradient(a,b, ga, gb, matched, occlu_l, occlu_r):
    #match these significant first
    from pstero import match; res, n_oc_l, n_oc_r, cont = match( a,b, ga, gb, matched, occlu_l, occlu_r)   
    return res, n_oc_l, n_oc_r, cont
    
def line2d(a,b): #a: left, b:right
    x = range(0,640)
    y1 = [ rgb2gray(v[0], v[1], v[2]) for v in a ]
    y2 = [ rgb2gray(v[0], v[1], v[2]) for v in b ]
    yc1 = [ rgb255_to_clab(v) for v in a ]
    yc2 = [ rgb255_to_clab(v) for v in b ]
    #if __display: plotDis2(x, y1 , y2) #more tuitive in visual
    
    d1 = [ y1[i+1]-y1[i] for i in range(0, 639) ]
    d2 = [ y2[i+1]-y2[i] for i in range(0, 639) ]
    d1 = [ 0 if abs(d1[i])<3 else abs(d1[i]) for i in range(0,639) ]
    d2 = [ 0 if abs(d2[i])<3 else abs(d2[i]) for i in range(0,639) ]
    dc1 = [ abs(delta_e_cie2000(yc1[i+1], yc1[i])) for i in range(0, 639) ]
    dc2 = [ abs(delta_e_cie2000(yc2[i+1], yc2[i])) for i in range(0, 639) ]
    if __display: plotDis2(range(0,639), d1 , d2) #more tuitive in visual
    
    #right's left half is all visible in a; a's second half is visible in b.
    # they have overlaps
    # 1. right's left half, sliding through a
    #d1 = [ y2[i] for i in range(0,320)]
    #r1 = match(d1, y1)  
    
    matched=[] # [x1, x2, bool(left match), bool (right match) ]
    occlu_l = [] #[x1, x2], x1<x2
    occlu_r = [] #[(x1, x2)], x1<x2
    while True:
        nm, nl, nr, cont = match_gradient(y1, y2, d1, d2, matched, occlu_l, occlu_r)
        if not nm:
            print('Abandoned this line.')
            break
        for x in nm: matched.append(x) #update all
        for x in nl: occlu_l.append(x)
        for x in nr: occlu_r.append(x)
            
        if not cont: break
    return

def plotDis2(x,y1, y2):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line = Line2D(x, y1, color="red")
    ax.add_line(line)
    line = Line2D(x, y2)
    ax.add_line(line)
    ax.set_xlim(min(x), max(x))
    ym = min( min(y1), min(y2))
    yx = max( max(y1), max(y2))
    ax.set_ylim(ym-5, yx+5)
    plt.show()
        
def plotDis(x,y):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line = Line2D(x, y)
    ax.add_line(line)
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    plt.show()
def test():
    [a,b, c, d,e, f] = read()
    line2d(a,b)
    line2d(c,d) #x: 144/118 (l/r)
    line2d(e,f) #x=88/50
if __name__ =='__main__':
    test()
