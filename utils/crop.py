import os
import numba
import numpy as np
import img3


@numba.njit(parallel=True)
def _crop(a, out, x0, y0):
    nx, ny, nz = out.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[x0+i, y0+j, k]


def crop(input_nrrd, coordinates, output_directory):
    x0, y0, x1, y1 = coordinates
    #print("inside crop:", coordinates)
    #print("x0:", x0)
    #print("y0:", y0)
    #print("x1:", x1)
    #print("y1:", y1)

    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(input_nrrd)
    img_stack = img3.read_input(input_nrrd, path, dtype, offset, shape)

    shape = img_stack.shape
    spacings = (dx, dy, dz)

    Lx = x1 - x0
    Ly = y1 - y0

    foutr = "%s/cropped_%s.raw" % ( output_directory, os.path.basename(input_nrrd) )
    foutn = "%s/cropped_%s.nrrd" % ( output_directory, os.path.basename(input_nrrd) )
    cropped = img3.mmap_create(foutr, img_stack.dtype, [Lx,Ly,shape[2]])
    img3.nrrd_write(foutn, foutr, cropped.dtype, cropped.shape, spacings)

    _crop(img_stack, cropped, x0, y0)

    return foutr, foutn    
