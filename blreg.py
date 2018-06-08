import numpy as np
import cython

#from same left lens
def imreg(data, x1, y1, iw=10, ih=10):
    bl1 = data['bl1']
    bl2 = data['bl2']
    px1 = data['px1']
    px2 = data['px2']
    w, h = 640, 400
    val = 0
    res = []
    for i in range(iw):
        ps = []
        for j in range(ih):
           d = round(abs(px1[x1+i,y1+j] - px2[x1+i, y1+j]),1)
           if d <=5: d= 0
           val +=  d*d
           res.append([x1+i, y1+i, d])
           ps.append(d)
        print (ps)
    res.sort(key=lambda k: k[2])
    print x1, y1, val, bl1[x1,y1], bl2[x1,y1], res
    return x1,y1, val, abs(bl1[x1,y1] - bl2[x1,y1])

