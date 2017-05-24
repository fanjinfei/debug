import math, os
import copy
from collections import defaultdict
import pdb

def align(a,b):
    return [a,b] if a<b else [b,a]

class NData:
    def __init__(self, ps, es, hull, tris):
        self.ps, self.es, self.hull, self.tris = ps, es, hull, tris
        
        p2es=defaultdict( list ) #may move to upper OBJ later
        p2ps=defaultdict(list)
        for [a,b,c] in tris:
            ls = [align(a,b), align(b,c), align(a,c)]
            for p in [a,b,c]:
                v = p2es[p]
                for li in ls:
                    if p in li: continue #NOT include radiation line
                    if li not in v:
                        v.append(li)
            for p in [a,b,c]:
                v = p2ps[p]
                for x in [a,b,c]:
                    if x==p or x in v: continue
                    v.append(x)
        self.p2es = p2es #with Triangle wrapping edge, and connection edges
        self.p2ps = p2ps #wrapping points
    def move(self, step, outline):
        return self.hull    
    def dist(self, i, j):
        (x1,y1) =  self.ps[i]
        (x2,y2) = self.ps[j]
        x1 = x1-x2
        y1 = y1 - y2
        return math.sqrt( x1*x1 + y1*y1)
