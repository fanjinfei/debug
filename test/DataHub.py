import math, os
import copy
from collections import defaultdict
import pdb
from DataFile import Flat

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
        if step==0:
            while True:
                inc, hull = self.easy_fix()
                if inc:
                    self.hull = hull
                else:
                    break
            outline = copy.deepcopy(hull)
            return outline, self.step1()
        else:
            return None, self.step2(outline)
    def step1(self):  # generate coarse outline of inner hops
        hull = copy.deepcopy(self.hull)
        hps, nps = self.getHpsNps(hull)
        
        #calc nps's best wrap line
        nes = []
        for x in nps:
            ls = [ (self.dist(a,x)+self.dist(b,x)-self.dist(a,b),x, a, b) 
                    for a,b in self.p2es[x] ]
            #ls.sort(key=lambda x: x[0])
            #sorted(ls, key=lambda x:x[0])
            # map, filter, reduce, generator(i.e., range(), GP for what?)
            ''' map can use list of functions '''
            ls = filter(lambda x: not( x[-1] in hps and x[-2] in hps and align(x[-1], x[-2]) not in hull), ls)
            
            l0 = min(ls, key=lambda x:x[0]) # what if ls2 empty
            nes.append(l0 )
        
        for _, c, a, b in nes:
            l1,l2 = align(a,c), align(b,c)
            if l1 not in hull:
                hull.append(l1)
            if l2 not in hull:
                hull.append(l2)

        return hull
    
    def step2(self, outline):  # merge the outline (alias hull) in step1
        flat = Flat(self.hull)
        return flat.run(outline)
    def easy_fix(self):
        hull = copy.deepcopy(self.hull)
        hps, nps = self.getHpsNps(hull)
                
        #calc nps's best wrap line
        min_hps = []
        for x in nps:
            ls = [ (self.dist(a,x)+self.dist(b,x)-self.dist(a,b),x, a, b) 
                    for a,b in self.p2es[x] ]
            #ls.sort(key=lambda x: x[0])
            #sorted(ls, key=lambda x:x[0])
            # map, filter, reduce, generator(i.e., range(), GP for what?)
            ''' map can use list of functions '''
            ls1 = filter(lambda x: not( x[-1] in hps and x[-2] in hps and align(x[-1], x[-2]) not in hull), ls)
            
            #ls2 = filter(lambda x: not( x[-1] in nps and x[-2] in nps), ls1) #avoid loop
            ls2 = ls1
            
            l0 = min(ls2, key=lambda x:x[0]) # what if ls2 empty
            if len(filter ( lambda x: x in hps, l0[-2:]) ) != 2:
                continue
            min_hps.append(l0 )

        #pick one and change the hull
        if not min_hps:
            return False, self.hull

        l0 = min(min_hps, key=lambda x: x[0])
        print('Single', l0)
        [_, c, a, b] = l0
        hull.remove( align(a,b))
        hull.append(align(a,c))
        hull.append(align(b,c))
        return True, hull
            
    def old_move_v1(self):
        hull = copy.deepcopy(self.hull)
        hps, nps = self.getHpsNps(hull)
        
        #calc nps's best wrap line
        min_hps = []
        xps = nps+hps
        for x in nps:
            ls = [ (self.dist(a,x)+self.dist(b,x)-self.dist(a,b),x, a, b) 
                    for a,b in self.p2es[x] ]
            #ls.sort(key=lambda x: x[0])
            #sorted(ls, key=lambda x:x[0])
            # map, filter, reduce, generator(i.e., range(), GP for what?)
            ''' map can use list of functions '''
            ls1 = filter(lambda x: not( x[-1] in hps and x[-2] in hps and align(x[-1], x[-2]) not in hull), ls)
            
            #ls2 = filter(lambda x: not( x[-1] in nps and x[-2] in nps), ls1) #avoid loop
            ls2 = ls1
            
            l0 = min(ls2, key=lambda x:x[0]) # what if ls2 empty
            if len(filter ( lambda x: x in xps, l0[-2:]) ) != 2:
                continue
            min_hps.append(l0 )
            if len(ls)!= len(ls2) and False:
                print(ls)
                print(ls1)
                print(ls2)
                os._exit(0)
        #print ('min_hps', min_hps[:5])
        
        #   
        #join neighbor section( b->a->hull) / a->b, b->(a,c), c->a / a->b, c->b, b->(a,c)/ ....
        #                       (a,b) / a,b,c / a,b,c
        ms1 = filter(lambda x: (x[-1] in nps and x[-2] in nps), 
                min_hps)
        ms2 = filter(lambda x: not (x[-1] in hps and x[-2] in hps), 
                list(set(min_hps)-set(ms1)))
                
        '''TODO: join above '''
        
        #simple test, TODO:join the neighbor section
        min_hps2 =filter(lambda x: (x[-1] in hps and x[-2] in hps), 
                list(set(min_hps)-set(ms1)-set(ms2)))
        
        #pick one and change the hull
        if min_hps2:
            ''' compare with ms1, ms2, YES! necessary! '''
            l0 = min(min_hps2, key=lambda x: x[0])
            print('Single', l0)
            [_, c, a, b] = l0
            hull.remove( align(a,b))
            hull.append(align(a,c))
            hull.append(align(b,c))
            return hull
            
        ret,hull = self.minSeg(ms1, ms2, hps, nps, hull)
        if ret:
            return hull

        ''' either do this last, OR joint upper filter'''
        #pdb.set_trace()
        #QCoreApplication::exec: The event loop is already running
        #print ('full min_hps', min_hps)
        print("******!!!!!!!!!!=================!!!!!!!!")
        #print 'exec1',min(min_hps, key=lambda x: x[0])
        hull = self.minPS(min_hps, hps, nps, xps, hull) #return hull

        return hull
    
    def minSeg(self, ms1, ms2, hps, nps, hull):
        ns = []
        segs = []
        for _,x,a,b in ms1:
            if a not in ns: ns.append(a)
            if b not in ns: ns.append(b)
            segs.append(align(a,b))
        
        ms3 = filter(lambda x: not( x[-1] in ns or x[-2] in ns or x[-3] in ns),
                ms2)
        
        if not ms1 and not ms3:
            return (False, hull)
        
        ''' no join yet (for continous rectangle)'''
        for _,x,a,b in ms3:
            if a in nps: segs.append(align(a,x))
            if b in nps: segs.append(align(b,x))
            if a in nps and b in nps:
                raise Exception('ber')
        
        lms = []
        for a,b in segs:
            def addSegs(x):
                c,d = x
                l1,l2,l3,l4 = self.dist(c,a), self.dist(d,b), self.dist(c,b), self.dist(d,a)
                l5,l6 = self.dist(b,a), self.dist(d,c)
                mms = [[l1+l2,a,b,c,d], [l3+l4, a,b,d,c]]
                l0 = min(mms)
                l0[0] = l0[0]+l5-l6
                return l0
            ls = map(addSegs, hull)
            l0 = min(ls, key=lambda x: x[0]) # can ommit if x[0]
            lms.append(l0)
        l0 = min(lms)
        print('Segment', l0)
        _,a,b,c,d = l0
        hull.remove( align(c,d))
        hull.append(align(a,c))
        hull.append(align(b,d))
        hull.append(align(a,b))
        return (True, hull)
    
    def minPS(self, segs, hps, nps, xps, hull):
        ms = []
        for y in nps:
            ls = map(lambda x: (self.dist(y, x[0])+
                        self.dist(y, x[1]) - self.dist(x[0], x[1]), y, x[0], x[1]),
                        hull)
            l0 = min(ls, key=lambda x: x[0]) # can ommit if x[0]
            ms.append(l0)
        lx,c,b,a= min(ms)
        print('minPS', (lx,c,b,a))
        hull.remove( align(a,b))
        hull.append(align(a,c))
        hull.append(align(b,c))
        return hull
    def dist(self, i, j):
        (x1,y1) =  self.ps[i]
        (x2,y2) = self.ps[j]
        x1 = x1-x2
        y1 = y1 - y2
        return math.sqrt( x1*x1 + y1*y1)
    def addEdge(self, es, a,b ,c):
        ls = [align(a,b), align(b,c), align(a,c)]
        for li in ls:
            if li not in es: es.append(li)
    def getHpsNps(self, hull):
        hps = []
        for [a,b] in hull:
            if a not in hps: hps.append(a)
            if b not in hps: hps.append(b)
        #print('hps:', hps)
        
        #find next to hps
        nps= []
        for x in hps:
            for y in self.p2ps[x]:
                if y not in hps and y not in nps:
                    nps.append(y)
        #print('nps', nps)
        return hps, nps        

'''
I worked as senior software developer at Fortinet Techonoliges (Canada)'s Ottawa office from 2007 to November, 2016. I wrote anti-spam software modules used in Email-server product Foritmail. The programming language I used are Python, C/C++, Perl, Java and shell script. 
The development host is Linux and Windows. To improve anti-spam, I developed a new algoirthm, leading data analysis team, embedded software team, clients, QA, documentation team.

I also wrote MS outlook plugins to report spam using Visual Studio and C# language, leading a team of developer, QA and document writer.
With my help, the Fortimail anti-spam got top 5 in VirusBulletin VBSpam tests.

Since I join STATCAN in November 2016, I worked on CKAN open-data project. I resolve customer issue promptly and correctly.
'''
'''
I worked on an anti-spam project at Fortinet Technologies (Canada).
I first collected spam samples from several customers in different countries. After research, I developed a prototype to verify the new algorithm.

After that, I wrote a technical report for management describing the new algorithm and initial test methods and test results. Later I lead a team of developer to implement it on product (Fortimail) and put it on corporate server to test for 6 months. During this period, I worked with QA to improve the feature and with document writer for user manuals. 

After the software release, I closely monitored the customer feedbacks and improved the product. The new feature can catch a lot new variants of spam timely and greatly helps customer.
'''
