import numpy as np
from mayavi import mlab
from tvtk.api import tvtk

#    3-----4-----5  y=1
#    | \ 1   \ 3 |
#    | 0 \ | 2 \ |
#    0-----1-----2  y=0
#   x=0   x=1   x=2

npoints = 6

def generate_points(z):
    return np.array([(0,0,z), (1,0,z), (2,0,z),
                     (0,1,z), (1,1,z), (2,1,z)], 'd')

@mlab.show
@mlab.animate(delay=250)
def anim():
    z = z0
    velocity = 0.5
    while True:
        z += velocity
        if z > 1 or z < -1:
            velocity *= -1
        points = generate_points(z)*1.1
        poly_data.points = points
        #poly_data.point_data.scalars = points[:,2]
        yield
z0 = 0.

triangles = np.array([(0,1,3), (1,4,3), (1,2,4), (2,5,4)], 'int32')
points = generate_points(z0)

fig = mlab.figure()

poly_data = tvtk.PolyData(points=generate_points(0), polys=triangles)
#poly_data.point_data.scalars = points[:,2]
#poly_data.point_data.scalars.name = "z"
surf = mlab.pipeline.surface(poly_data)

anim()
