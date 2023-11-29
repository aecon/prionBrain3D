import os
import sys
import mmap
import time
import numba
import pickle
import numpy as np
import multiprocessing
from skimage.morphology import remove_small_objects, remove_small_holes, ball

import img3
from utils.dataset import Dataset

me = "segmentation.py"


def nrrd_details(fnrrd):
    nrrd        = img3.nrrd_read(fnrrd)
    dtype       = nrrd["type"]
    path        = nrrd["path"]
    shape       = nrrd["sizes"]
    offset      = nrrd.get("byte skip", 0)
    dx, dy, dz  = nrrd.get("spacings")
    return dtype, path, shape, offset, dx, dy, dz


def read_stride(argsk):
    if len(argsk) != 3:
        sys.stderr.write("%s: -k needs three arguments\n" % me)
        sys.exit(1)
    kx, ky, kz = argsk
    return kx, ky, kz


def read_input(argsi, me, path, dtype, offset, shape):
    try:
        a0 = np.memmap(path, dtype, 'r', offset=offset, shape=shape, order='F')
    except FileNotFoundError:
        sys.stderr.write("%s: file not found '%s'\n" % (me, argsi))
        sys.exit(1)
    except ValueError:
        sys.stderr.write("%s: wrong size/type '%s'\n" % (me, argsi))
        sys.exit(1)
    return a0


@numba.njit(parallel=True)
def divide(a1, a2, keep, out):
    nx, ny, nz = a1.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a1[i, j, k] / a2[i, j, k] if keep[i, j, k] > 0 else 0


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
def binary(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 1 if a[i, j, k] > 0 else 0


@numba.njit(parallel=True)
def mask_array(a, keep, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[i, j, k] if keep[i, j, k] > 0 else 0


@numba.njit(parallel=True)
def copy(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = a[i, j, k]


class Arguments:
    def __init__(self):
        # Background equalization
        self.Imax = 1000
        self.Imin = 200

        # Defaults
        self.w = 50
        self.log = 0.3
        self.Vmin = 27
        self.Ibmax = 2.0
        self.Ibmin = 1.8
        self.s = [1,1,1]
        self.ro = 27
        self.rh = 200

        # Flags
        self.p = False
        self.v = True



def segment(dataset):

    args = Arguments()
 
    Verbose = args.v
    Parallel = args.p

    input_file = dataset.input_nrrd
    output_directory = dataset.output_directory

    
    # Read RAW data
    dtype, path, shape, offset, dx, dy, dz = nrrd_details(input_file)
    img_stack = read_input(input_file, me, path, dtype, offset, shape)
    
    # Stride RAW data
    sx, sy, sz = read_stride(args.s)
    dx, dy, dz = sx*dx, sy*dy, sz*dz
    img_stack = img_stack[::sx, ::sy, ::sz]
    shape = img_stack.shape
    spacings = (dx, dy, dz)
    if Verbose:
        sys.stderr.write("%s: shape: %d %d %d\n" % (me, shape[0], shape[1], shape[2]))
    
    start = time.time()
    
    # Create new arrays
    print("create new arrays")
    odir = "%s/%s" % (output_directory, "segment")
    if not os.path.exists(odir):
        os.makedirs(odir)
    keep    = img3.mmap_create("%s/mask.raw" % odir, np.dtype("uint8"), shape)
    keepE   = img3.mmap_create("%s/mask_erosion.raw" % odir, np.dtype("uint8"), shape)
    tmp8    = img3.mmap_create("%s/tmp8.raw" % odir, np.dtype("uint8"), shape)
    segmented = img3.mmap_create("%s/segmented.raw" % odir, np.dtype("uint8"), shape)
    tmp32a  = img3.mmap_create("%s/tmp32a.raw" % odir, np.dtype("float32"), shape)
    tmp32b  = img3.mmap_create("%s/tmp32b.raw" % odir, np.dtype("float32"), shape)
    labels  = img3.mmap_create("%s/labels.raw" % odir, np.dtype(np.int64), shape)
    work    = img3.mmap_create("%s/work.raw" % odir, np.dtype(np.int64), shape)
    denoised= img3.mmap_create("%s/denoised.raw" % odir, np.dtype("float32"), shape)
    
    img3.nrrd_write("%s/segmented.nrrd" % odir, "%s/segmented.raw" % odir, segmented.dtype, segmented.shape, spacings)

    dataset.segmented_nrrd = "%s/segmented.nrrd" % odir

    
    Imax = args.Imax
    Imin = args.Imin
    ro   = args.ro
    rh   = args.rh


    def mask(k):
        img0 = img_stack[:, :, k]
    
        # working array
        img = np.zeros((np.shape(img0)))
        img[:,:] = img0[:,:]
    
        # mask + remove holes and small objects from mask
        keep0 = np.zeros(np.shape(img), dtype=bool)
        keep0[img>=Imin] = 1
        remove_small_objects(keep0, min_size=ro, out=keep0)
        remove_small_holes(keep0, area_threshold=rh, out=keep0)
    
        keep[:,:,k] = keep0.astype(keep.dtype)


    print("generate mask (multiprocessing.Pool)")
    if Parallel:
        with multiprocessing.Pool() as pool:
            pool.map(mask, range(shape[2]))
    else:
        for k in range(shape[2]):
            mask(k)

    print("copy (numba)")
    copy(keep, out=tmp8)
    nstep = 10
    print("erode mask (img3.erosion)")
    img3.erosion(tmp8, nstep, keepE)

    print("copy (numba)")
    copy(img_stack, out=tmp32a)
    print("img3.memset(tmp32b, 0)")
    img3.memset(tmp32b, 0)
    print("clip Imax (numba)")
    clip(tmp32a, Imax, tmp32b)

    print("background smoothing (img3.gauss)")
    sigma = args.w
    img3.gauss(tmp32b, keep, sigma, tmp32a)

    print("intensity normalization (numba)")
    divide(img_stack, tmp32a, keep, out=tmp32b)

    print("img3.memset(tmp32a, 0)")
    img3.memset(tmp32a, 0)
    print("denoise (img3.gauss)")
    sigma = 1
    img3.gauss(tmp32b, keep, sigma, tmp32a)

    print("mask denoised (numba)")
    mask_array(tmp32a, keep, tmp32b)

    print("copy (numba)")
    copy(tmp32b, out=denoised)


    print("internal from denoised (numba)")
    uclip(tmp32a, args.Ibmin, tmp32b)

    print("0/1 internal")
    binary(tmp32b, tmp8)

    print("img3.memset(labels, 0)")
    img3.memset(labels, 0)
    print("labels (img3.label)")
    Nc = img3.labels(tmp8, labels, work)
    sys.stderr.write("  Nc(all): %d\n" % Nc)

    print("img3.remove_small_objects")
    Nc = img3.remove_small_objects(labels, args.Vmin, work)
    sys.stderr.write("  Nc(Vmin): %d\n" % Nc)

    print("0/1 segmented")
    binary(labels, segmented)

    print("candidate cells (img3.objects)")
    lst = img3.objects(labels, Nc)

    print("save candidate list to pickle")
    with open("%s/lst.pkl" % odir,'wb') as fl:
        pickle.dump(lst, fl)

    print("filter on Imax (for loop)")
    lst1 = []
    for l in lst:
        Intensities = denoised[l[:,0], l[:,1], l[:,2]]
        if np.max(Intensities) >= args.Ibmax:
            lst1.append(l)
        else:
            segmented[l[:,0], l[:,1], l[:,2]] = 0
    Nc = len(lst1)
    sys.stderr.write("  Nc(Imax): %d\n" % Nc)

    print("done.")

