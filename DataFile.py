import math, os
import copy
from collections import defaultdict
import gzip;

def align(a,b):
    return [a,b] if a<b else [b,a]

class DFile:
    def __init__(self, filename):
        state = -1
        data = []
        with gzip.open(filename) as fin:
            for line in fin:
                if state == -1:
                    if 'NODE_COORD_SECTION' in line:
                        state = 0
                elif state ==0:
                    if 'EOF' in line:
                        state = 1
                        break
                    _,x,y = line.split(' ')
                    x,y= float(x.strip()), float(y.strip())
                    data.append([x,y])
        print('read', filename, len(data))
        self.data = data
