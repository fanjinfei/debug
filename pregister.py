#!/usr/bin/python

from numpy import *
from math import sqrt

# Input: expects 3xN matrix of points
# Returns R,t
# R = 3x3 rotation matrix
# t = 3x1 column vector

def rigid_transform_3D(A, B):
    assert len(A) == len(B)

    num_rows, num_cols = A.shape;

    if num_rows != 3:
        raise Exception("matrix A is not 3xN, it is {}x{}".format(num_rows, num_cols))

    [num_rows, num_cols] = B.shape;
    if num_rows != 3:
        raise Exception("matrix B is not 3xN, it is {}x{}".format(num_rows, num_cols))

    # find mean column wise
    centroid_A = mean(A, axis=1)
    centroid_B = mean(B, axis=1)

    # subtract mean
    Am = A - tile(centroid_A, (1, num_cols))
    Bm = B - tile(centroid_B, (1, num_cols))

    # dot is matrix multiplication for array
    H = Am * transpose(Bm)

    # find rotation
    U, S, Vt = linalg.svd(H)
    R = Vt.T * U.T

    # special reflection case
    if linalg.det(R) < 0:
        print("det(R) < R, reflection detected!, correcting for it ...\n");
        Vt[2,:] *= -1
        R = Vt.T * U.T

    t = -R*centroid_A + centroid_B

    return R, t

# Test with random data

# Random rotation and translation
R = mat(random.rand(3,3))
t = mat(random.rand(3,1))

# make R a proper rotation matrix, force orthonormal
U, S, Vt = linalg.svd(R)
R = U*Vt

# remove reflection
if linalg.det(R) < 0:
   Vt[2,:] *= -1
   R = U*Vt

# number of points
n = 10

A = mat(random.rand(3, n));
B = R*A + tile(t, (1, n))

Bx = B.copy()
rows, cols = Bx.shape
for i in range(0, rows):
    for j in range(0, cols):
        idx = j*rows+j
#        v = Bx.item(idx) + random.uniform(-0.01, +0.01)
        Bx[i,j] +=  random.uniform(-0.01, +0.01)
print("Bx")
print(Bx)
print("")
# Recover R and t
ret_R, ret_t = rigid_transform_3D(A, Bx)

# Compare the recovered R and t with the original
B2 = (ret_R*A) + tile(ret_t, (1, n))

# Find the root mean squared error
err = B2 - B
err = multiply(err, err)
err = sum(err)
rmse = sqrt(err/n);

print("Points A")
print(A)
print("")

print("Points B")
print(B)
print("")

print("Ground truth rotation")
print(R)

print("Recovered rotation")
print(ret_R)
print("")

print("Ground truth translation")
print(t)

print("Recovered translation")
print(ret_t)
print("")

print("RMSE:", rmse)

#if rmse < 1e-5:
if rmse < 1e-2:
    print("Everything looks good!\n");
else:
    print("Hmm something doesn't look right ...\n");
    
X = mat([[0.64724042, 0.35758181, 0.9512442,  1.29723368, 0.92860612, 0.65345024,
  0.80022358, 0.73112236, 1.0980026,  0.52053852],
 [1.22940512, 1.66716644, 1.15930556, 1.22476976, 1.33246935, 1.42477522,
  1.5600748,  1.25985761, 1.22146866, 1.75895506],
 [0.37247002, 0.77672062, 0.49042198, 0.37532438, 1.37755089, 0.47549959,
  1.1263332,  0.23312056, 1.03766375, 0.87879653]])
U, S, Vt = linalg.svd(X)
print(U)
print(S)
print(Vt)

