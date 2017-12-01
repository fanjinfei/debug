import math, os
import copy
from collections import defaultdict
import gzip;

def align(a,b):
    return [a,b] if a<b else [b,a]

class Flat:
    def __init__(self, segs):
        #given coarse hull
        self.segs = segs
    def run(self, outline):
        nes = []
        lines = self.getLines(self.segs)
        lines = self.removeDead(lines)
        
        for line in lines:
            for i in range(0, len(line)-1):
                a,b = line[i], line[i+1]
                nes.append(align(a,b))
        
        #rebuild
        lines = self.getLines(nes)
        
        #get line loops agains outliner
        
        #DEBUG: temporary use
        return nes
    def getLoops(self, lines, outline):
        eps = []
        for a,b in outline:
            if a not in eps: eps.append(a)
            if b not in eps: eps.append(b)
        outls, inls = [],[]
        for e in lines:
            isOutline = True
            for p in e:
                if p not in eps:
                    isOutline = False
                    break
            if isOutline:
                outls.append(e)
            else:
                inls.append(e)
        loops = []
        seg = None
        while True:
            break
    def removeDead(self, lines):
        while True:
            p2c = defaultdict(int)
            for e in lines:
                a,b = e[0], e[-1]
                p2c[a] += 1
                p2c[b] += 1
            to_del = []
            for e in lines:
                a,b = e[0], e[-1]
                if p2c[a] ==1 or p2c[b] ==1:
                    to_del.append(e)
            if not to_del:
                break
            for e in to_del:
                lines.remove(e)

        return lines
    def getLines(self, segs):
        es = copy.deepcopy(segs)
        p2c = defaultdict(int)
        for a,b in es:
            p2c[a] += 1
            p2c[b] += 1
        lines = []
        line = []
        while len(es) > 0:
            if not line:
                line = es[0]
                es.remove(line)
            a,b= line[0], line[-1]
            found = False
            for c,d in es:
                if a==c and p2c[a] ==2:
                    line.insert(0,d)
                    found = True
                elif a==d and p2c[a] ==2:
                    line.insert(0,c)
                    found = True
                elif b==c and p2c[b] ==2:
                    line.append(d)
                    found = True
                elif b==d and p2c[b] ==2:
                    line.append(c)
                    found = True
                if found == True:
                    es.remove([c,d])
                    break
            if not found:
                lines.append(line)
                line = []
        return lines
                    
                
class DFile:
    def __init__(self, filename):
        if filename[-7:] != '.tsp.gz':
            try:
                self.data = []
                if os.path.exists(filename):
                    self.read_opt(filename)
            except:
                pass
            return
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
    def read_opt(self, filename):
        state = -1
        data = []
        with gzip.open(filename) as fin:
            for line in fin:
                if state == -1:
                    if 'TOUR_SECTION' in line:
                        state = 0
                elif state ==0:
                    if 'EOF' in line:
                        state = 1
                        break
                    x = int(line.strip()) - 1
                    if x == -2: break
                    data.append(x)
        print('read', filename, len(data))
        for i in range(-1, len(data)-1):
            self.data.append([data[i], data[i+1]])

