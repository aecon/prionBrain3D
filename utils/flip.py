import os
import sys
import numba
import numpy as np
import img3


@numba.njit(parallel=True)
def _flipx(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[(nx-i-1), j, k]


@numba.njit(parallel=True)
def _flipz(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[i, j, (nz-k-1)]


def get_filenames(input_nrrd, output_directory):
    """
    Returns paths to the generated raw and nrrd files
    """
    basename = os.path.basename(input_nrrd)
    raw_path  = "%s/flip_%s.raw"  % ( output_directory, basename )
    nrrd_path = "%s/flip_%s.nrrd" % ( output_directory, basename )
    return raw_path, nrrd_path


def _prepare_data(input_nrrd, output_directory):
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(input_nrrd)
    raw = img3.read_input(input_nrrd, path, dtype, offset, shape)

    fout_raw, fout_nrrd = get_filenames(input_nrrd, output_directory)

    flip_raw = img3.mmap_create(fout_raw, raw.dtype, raw.shape)
    img3.nrrd_write(fout_nrrd, fout_raw, flip_raw.dtype, flip_raw.shape, (dx,dy,dz))

    return raw, flip_raw, fout_raw, fout_nrrd


def flip_horizontally(input_nrrd, output_directory):
    raw, flip_raw, fout_raw, fout_nrrd = _prepare_data(input_nrrd, output_directory)
    _flipx(raw, flip_raw)
    return fout_raw, fout_nrrd


def flip_stack(input_nrrd, output_directory):
    raw, flip_raw, fout_raw, fout_nrrd = _prepare_data(input_nrrd, output_directory)
    _flipz(raw, flip_raw)
    return fout_raw, fout_nrrd


