import json
def read():
    with open('/tmp/lr.json') as json_file:
        data = json.load(json_file)
        return data

def rgb2gray(R,G,B):
    return 0.21*R + 0.72*G + 0.07*B
    
def match(d1, y1): #d1: right side's first half, y1: full left side
    from scipy.fftpack import fft
    N=320
    y = fft(d1)
    print (y)
    return
    
def line2d(a,b): #a: left, b:right
    x = range(0,640)
    y1 = [ rgb2gray(v[0], v[1], v[2]) for v in a ]
    y2 = [ rgb2gray(v[0], v[1], v[2]) for v in b ]
    plotDis2(x, y1 , y2) #more tuitive in visual
    
    d1 = [ y1[i+1]-y1[i] for i in range(0, 639) ]
    d2 = [ y2[i+1]-y2[i] for i in range(0, 639) ]
    d1 = [ 0 if abs(d1[i])<3 else d1[i] for i in range(0,639) ]
    d2 = [ 0 if abs(d2[i])<3 else d2[i] for i in range(0,639) ]
    plotDis2(range(0,639), d1 , d2) #more tuitive in visual
    
    #right's left half is all visible in a; a's second half is visible in b.
    # they have overlaps
    # 1. right's left half, sliding through a
    d1 = [ y2[i] for i in range(0,320)]
    r1 = match(d1, y1)  
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
    [a,b] = read()
    line2d(a,b)
if __name__ =='__main__':
    test()
