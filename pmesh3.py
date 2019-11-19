import numpy as np
from numpy import sin,cos,pi,sqrt # makes the code more readable
import pylab as plt
from mayavi import mlab # or from enthought.mayavi import mlab
from scipy.optimize import newton
import time

mlab.clf()
phi, theta = np.mgrid[0:np.pi:11j, 0:2*np.pi:11j]
x = np.sin(phi) * np.cos(theta)
y = np.sin(phi) * np.sin(theta)
z = np.cos(phi)
mlab.mesh(x, y, z)
mlab.mesh(x, y, z, representation='wireframe', color=(0, 0, 0))
mlab.show()
#time.sleep(10)
