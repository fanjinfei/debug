import numpy as np
from numpy import sin,cos,pi,sqrt # makes the code more readable
import pylab as plt
from mayavi import mlab # or from enthought.mayavi import mlab
from mayavi.mlab import *
from scipy.optimize import newton
import time, os

#apt install libgdal20 python3-gdal pyqt5
#pip install gdal==2.4.0 (ubuntu 18.04LTS bionic)

def test_triangular_mesh():
    """An example of a cone, ie a non-regular mesh defined by its
        triangles.
    """
    n = 8
    t = np.linspace(-np.pi, np.pi, n)
    z = np.exp(1j * t)
    x = z.real.copy()
    y = z.imag.copy()
    z = np.zeros_like(x)

    triangles = [(0, i, i + 1) for i in range(1, n)]
    x = np.r_[0, x]
    y = np.r_[0, y]
    z = np.r_[1, z]
    t = np.r_[0, t]

    return triangular_mesh(x, y, z, triangles, scalars=t)

test_triangular_mesh()    
mlab.show()
os._exit()

mlab.clf()
phi, theta = np.mgrid[0:np.pi:11j, 0:2*np.pi:11j]
x = np.sin(phi) * np.cos(theta)
y = np.sin(phi) * np.sin(theta)
z = np.cos(phi)
mlab.mesh(x, y, z)
mlab.mesh(x, y, z, representation='wireframe', color=(0, 0, 0))
mlab.show()
#time.sleep(10)




import gdal
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib import cm
#import matplotlib.pyplot as plt
from mayavi import mlab
import numpy as np

# maido is the name of a mountain
# tipe is the name of a french school project

# 1) opening maido geotiff as an array
maido = gdal.Open('dem_maido_tipe.tif')
dem_maido = maido.ReadAsArray()

# 2) transformation of coordinates
columns = maido.RasterXSize
rows = maido.RasterYSize
gt = maido.GetGeoTransform()
ndv = maido.GetRasterBand(1).GetNoDataValue()

x = (columns * gt[1]) + gt[0]
y = (rows * gt[5]) + gt[3]

X = np.arange(gt[0], x, gt[1])
Y = np.arange(gt[3], y, gt[5])

# 3) creation of a simple grid without interpolation
X, Y = np.meshgrid(X, Y)

#Mayavi requires col, row ordering. GDAL reads in row, col (i.e y, x) order
dem_maido = np.rollaxis(dem_maido,0,2)
X = np.rollaxis(X,0,2)
Y = np.rollaxis(Y,0,2)

print (columns, rows, dem_maido.shape)
print (X.shape, Y.shape)

# 4) deleting the "no data" values
dem_maido = dem_maido.astype(np.float32)
dem_maido[dem_maido == ndv] = np.nan #if it's NaN, mayavi will interpolate

# delete the last column
dem_maido = np.delete(dem_maido, len(dem_maido)-1, axis = 0)
X = np.delete(X, len(X)-1, axis = 0)
Y = np.delete(Y, len(Y)-1, axis = 0)

# delete the last row
dem_maido = np.delete(dem_maido, len(dem_maido[0])-1, axis = 1)
X = np.delete(X, len(X[0])-1, axis = 1)
Y = np.delete(Y, len(Y[0])-1, axis = 1)

# 5) plot the raster
#fig, axes = plt.subplots(subplot_kw={'projection': '3d'})
#surf = axes.plot_surface(X, Y, dem_maido, rstride=1, cstride=1, cmap=cm.gist_earth,linewidth=0, antialiased=False)
#plt.colorbar(surf)  # adding the colobar on the right
#plt.show()

surf = mlab.surf(X, Y, dem_maido, warp_scale="auto")
mlab.show()


