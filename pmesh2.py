from stl import mesh
import math
import numpy
from matplotlib import colors as mcolors
#apt install python3-tk numpy-stl
#https://github.com/WoLpH/numpy-stl/

def cc(arg):
#    return mcolors.to_rgba(arg, alpha=0.6)
    return mcolors.to_rgba(arg, alpha=numpy.random.random())

# Create 3 faces of a cube
data = numpy.zeros(6, dtype=mesh.Mesh.dtype)

# Top of the cube
data['vectors'][0] = numpy.array([[0, 1, 1],
                                  [1, 0, 1],
                                  [0, 0, 1]])
data['vectors'][1] = numpy.array([[1, 0, 1],
                                  [0, 1, 1],
                                  [1, 1, 1]])
# Front face
data['vectors'][2] = numpy.array([[1, 0, 0],
                                  [1, 0, 1],
                                  [1, 1, 0]])
data['vectors'][3] = numpy.array([[1, 1, 1],
                                  [1, 0, 1],
                                  [1, 1, 0]])
# Left face
data['vectors'][4] = numpy.array([[0, 0, 0],
                                  [1, 0, 0],
                                  [1, 0, 1]])
data['vectors'][5] = numpy.array([[0, 0, 0],
                                  [0, 0, 1],
                                  [1, 0, 1]])

# Since the cube faces are from 0 to 1 we can move it to the middle by
# substracting .5
data['vectors'] -= .5

# Generate 4 different meshes so we can rotate them later
meshes = [mesh.Mesh(data.copy()) for _ in range(5)]

# Rotate 90 degrees over the Y axis
meshes[0].rotate([0.0, 0.5, 0.0], math.radians(90))

# Translate 2 points over the X axis
meshes[1].x += 2
meshes[4].x += 10

# Rotate 90 degrees over the X axis
meshes[2].rotate([0.5, 0.0, 0.0], math.radians(90))
# Translate 2 points over the X and Y points
meshes[2].x += 2
meshes[2].y += 2

# Rotate 90 degrees over the X and Y axis
meshes[3].rotate([0.5, 0.0, 0.0], math.radians(90))
meshes[3].rotate([0.0, 0.5, 0.0], math.radians(90))
# Translate 2 points over the Y axis
meshes[3].y += 2

#add more cube to meshes to see the performance 100*100
es = []
for x in range(5):
    for y in range(5):
        for z in range(5):
            e = mesh.Mesh(data.copy())
            e.x += 2*(x+2)
            e.y += 4*(y+4)
            e.z += 8*(z+8)
            es.append(e)

for e in es:
    meshes.append(e)
print(len(meshes))

m2 = []
for i in range (50): #very slow
  for j in range(50):
    d1 = numpy.array([[i, j, 1],[i+1, j+1, 1], [i, j+1, 1]])
    d2 = numpy.array([[i, j, 1],[i+1, j+1, 1], [i+1, j, 1]])
    d = numpy.zeros(2, dtype=mesh.Mesh.dtype)
    d['vectors']=[d1, d2]
    m2.append(mesh.Mesh(d))
    
m2 = []
d = numpy.zeros(50*50*2, dtype=mesh.Mesh.dtype)
for i in range (50): #still slow
  for j in range(50):
    d1 = numpy.array([[i, j, 1],[i+1, j+1, 1], [i, j+1, 1]])
    d2 = numpy.array([[i, j, 1],[i+1, j+1, 1], [i+1, j, 1]])
    d['vectors'][i*50+j] =d1
    d['vectors'][i*50+j+1] =d2
m2.append(mesh.Mesh(d))

meshes

# Optionally render the rotated cube faces
from matplotlib import pyplot
from mpl_toolkits import mplot3d

def plot_3D(img, threshold=-400):
	verts, faces = measure.marching_cubes(img, threshold)

	fig = plt.figure(figsize=(10, 10))
	ax = fig.add_subplot(111, projection='3d')

	mesh = Poly3DCollection(verts[faces], alpha=0.1)
	face_color = [0.3, 0.5, 0.8]
	#mesh.set_facecolor(face_color)
	ax.add_collection3d(mesh)

	ax.set_xlim(0, img.shape[0])
	ax.set_ylim(0, img.shape[1])
	ax.set_zlim(0, img.shape[2])

	pyplot.show() 
# Create a new plot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# Render the cube faces
facecolors=[cc('r'), cc('g'), cc('b'), cc('y')]
facecolors=[cc('r'), cc('g'), cc('b'), cc('y')]
for m in meshes:
  for col in m.vectors:
    mesh = mplot3d.art3d.Poly3DCollection([col], alpha=0.6)
    face_color = [numpy.random.random(), numpy.random.random(), numpy.random.random()]
    #mesh.set_facecolor(face_color)
    axes.add_collection3d(mesh)

# Auto scale to the mesh size
scale = numpy.concatenate([m.points for m in meshes]).flatten(-1)
print(scale)
#axes.auto_scale_xyz(scale, scale, scale)
'''axes.set_xlim3d(0,15, 2)
axes.set_ylim3d(0,15)
axes.set_zlim3d(0,15)
'''
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()
