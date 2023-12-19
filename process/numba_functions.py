import os
import numba
import numpy as np


# Set number of threads
nthreads = 120
os.environ["OMP_NUM_THREADS"] = "%s" % nthreads # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = "%s" % nthreads # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "%s" % nthreads # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "%s" % nthreads # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "%s" % nthreads # export NUMEXPR_NUM_THREADS=6
numba.set_num_threads = nthreads


@numba.njit(parallel=True)
def copy(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[i, j, k]

@numba.njit(parallel=True)
def clip(a, value, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[i, j, k] if a[i, j, k] <= value else value

@numba.njit(parallel=True)
def uclip(a, value, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[i, j, k] if a[i, j, k] >= value else 0

@numba.njit(parallel=True)
def divide(a1, a2, keep, out):
    nx, ny, nz = a1.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a1[i, j, k] / a2[i, j, k] if keep[i, j, k] > 0 else 0

@numba.njit(parallel=True)
def remove_area(a, out, value):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 0 if a[i, j, k] == value else out[i, j, k]

@numba.njit(parallel=True)
def construct_mask(a, out, value):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 0 if a[i, j, k] == value else out[i, j, k]

@numba.njit(parallel=True)
def construct_mask_0(a, out, value):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 0 if a[i, j, k] == value else 1

@numba.njit(parallel=True)
def binary_value(a, out, value):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 1 if a[i, j, k] >= value else 0

@numba.njit(parallel=True)
def binary(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 1 if a[i, j, k] > 0 else 0

