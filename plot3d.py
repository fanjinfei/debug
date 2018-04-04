import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

point  = np.array([1, 2, 3])
normal = np.array([1, 1, 2])

point2 = np.array([10, 50, 50])

# a plane is a*x+b*y+c*z+d=0
# [a,b,c] is the normal. Thus, we have to calculate
# d and we're set
d = -point.dot(normal)

# create x,y
xx, yy = np.meshgrid(range(10), range(10))

# calculate corresponding z
z = (-normal[0] * xx - normal[1] * yy - d) * 1. /normal[2]

def draw1():
    # plot the surface
    plt3d = plt.figure().gca(projection='3d')
    plt3d.plot_surface(xx, yy, z, alpha=0.2)

    # Ensure that the next plot doesn't overwrite the first plot
    ax = plt.gca()
    ax.hold(True)

    ax.scatter(point2[0], point2[1], point2[2], color='green')

def draw2():
    # Create the figure
    fig = plt.figure()

    # Add an axes
    ax = fig.add_subplot(111,projection='3d')

    # plot the surface
    ax.plot_surface(xx, yy, z, alpha=0.2)

    # and plot the point 
    ax.scatter(point2[0] , point2[1] , point2[2],  color='green')

#draw1()
draw2()
plt.show()
