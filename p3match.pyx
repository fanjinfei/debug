# cython: infer_types=True
import numpy as np
import cython
DTYPE = np.intc
#DTYPE = np.float64
#ctypedef np.float64_t DTYPE_t

'''

@cython.cdivision(True)
cdef inline double recip_square2(double i):
    return 1./(i*i)
'''
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef inline double calculate_diff3(int[:,::1] pix1, int[:,::1]  pix2, int x1, int y1, int x2, int y2): #rectangle, SAD- sum of absolute difference
#, int w=9, int h =9
    cdef double d = 0.0
    cdef double m = 0.0
    cdef int i, j
    for i in range(21):
#        for j in range(h):
#            m = abs(pix1[x1+i, y1+j] - pix2[x2+i, y2+j])
            m = abs(pix1[x1+i, y1] - pix2[x2+i, y2])
            d += m*m
    return d #histogram diff?

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef inline int calculate_match(int[:,::1] px1, int[:,::1] px2, int x1, int y1, int y_offset, int edge=10, int max_right=100, int verbose=0): 
    cdef int w = 640
    cdef int h = 640
    #edge = 10 #2*edge+1 = block size
    cdef int bsz = 2*edge +1
    cdef int x2 = x1
    cdef int y2 = y1+y_offset
    cdef float val = 0.0
    cdef float threshold = 0.0 #mininum matching
    cdef int max_shift = min(max_right, x1-edge-1)
    cdef int i, k
    cdef int rx = -1
    cdef double rval = 0.0
    cdef double sad

    for i in range(max_shift):
        #sad, hd = calculate_diff2(px1, px2, x1-edge, y1-edge, x1-i-edge, y2-edge, bsz)
        #sad, hd = calculate_diff3(px1, px2, x1-edge, y1-1, x1-i-edge, y2-1, bsz, 3)
        #sad = calculate_diff3(px1, px2, x1-edge, y1-1, x1-i-edge, y2-1, bsz, 3)
        #sad = calculate_diff3(px1, px2, x1-edge, y1, x1-i-edge, y2, bsz, 1)
        sad = calculate_diff3(px1, px2, x1-edge, y1, x1-i-edge, y2)
        if rx == -1 or rval > sad:
            rx = x1 - i
            rval = sad
    return rx

#ouput 3D PC, zero in left lens
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
#def match_lr(em1, array, int [:,:] px1, int [:,:] px2, int w, int h, int y_offset, int edge=10):
def match_lr(em1, array, int [:,::1] px1, int [:,::1] px2, int w, int h, int y_offset, int edge=10):
    #match each of the p1 in px1 to p2 in px2, sort them in order
    #do not calculate the edge size(10)
    cdef int rows = array.shape[0]
    cdef int cols = array.shape[1]
    out = np.zeros([rows, cols], dtype = DTYPE)
    print "cython size", rows, cols

    #res = []
    cdef int j, i, mi

    for j in range(16, h-edge-2):
        for i in range(14, w-edge-2):
            if em1[j][i] == 0: continue
            mi = calculate_match(px1, px2, i, j, y_offset, edge, 100) #100
            #res.append([i, j, mi, j+y_offset, 100])
            out[i,j]=mi
    #print 'count edge points', count_e
    return out

