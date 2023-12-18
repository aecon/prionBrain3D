import os
import sys
import nrrd
import numpy as np

import img3
from process.numba_functions import *
from process.ABA_regions import ABAregion_to_ID
from utils.dataset import Dataset


def segment(dataset):

    spacings    = dataset.pixel_sizes   # pixel size in micro-meters
    sigmaB      = 10                    # standard deviation for background estimation
    sigmaD      = 1                     # standard deviation for denoising
    Imax        = 5000                  # max. intensity clip for background estimation
    Imin        = 1.08                  # min. voxel intensity for segmentation
    Vmin        = 14                    # min. volume per object (3D star: 4+4+6=14)
    Nerosion    = 2                     # number of erosion steps
    Icmax       = 1.10                  # minimum maximum intensity per cell

    input_nrrd = dataset.input_nrrd
    output_directory = dataset.output_directory
    annotation_atlas_nrrd = dataset.registered_annotation_atlas

    dataset.denoised_nrrd = "%s/%s_denoised.nrrd" % (output_directory, os.path.basename(input_nrrd))

    print("(segment) Loading input data ...")
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(input_nrrd)
    img_stack = img3.read_input(input_nrrd, path, dtype, offset, shape)

    print("(segment) Loading transformed annotation atlas")
    annotation_atlas, _ = nrrd.read(annotation_atlas_nrrd)

    print("(segment) creating tmp work arrays ...")
    tmp8    = img3.mmap_create("%s/tmp_8.raw"    % output_directory, np.dtype("uint8"), shape)
    keep    = img3.mmap_create("%s/tmp_mask.raw" % output_directory, np.dtype("uint8"), shape)
    tmp32a  = img3.mmap_create("%s/tmp_32a.raw" % output_directory, np.dtype("float32"), shape)
    tmp32b  = img3.mmap_create("%s/tmp_32b.raw" % output_directory, np.dtype("float32"), shape)
    labels  = img3.mmap_create("%s/tmp_labels.raw" % output_directory, np.dtype(np.int64), shape)
    work    = img3.mmap_create("%s/tmp_work.raw"   % output_directory, np.dtype(np.int64), shape)
    denoised= img3.mmap_create("%s/%s_denoised.raw" % (output_directory, os.path.basename(input_nrrd)), np.dtype("float32"), shape)
    img3.nrrd_write("%s/%s_denoised.nrrd" % (output_directory, os.path.basename(input_nrrd)), "%s/%s_denoised.raw" % (output_directory, os.path.basename(input_nrrd)), np.dtype("float32"), shape, spacings)


    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Normalization and Denoise
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    print("(segment) make keep mask")
    binary_eq_value(annotation_atlas, keep, 0)

    print("(segment) copy (numba)")
    copy(img_stack, out=tmp32a)

    print("(segment) img3.memset(tmp32b, 0)")
    img3.memset(tmp32b, 0)

    print("(segment) clip Imax (numba)")
    clip(tmp32a, Imax, tmp32b)

    print("(segment) background smoothing (img3.gauss)")
    img3.gauss(tmp32b, keep, sigmaB, tmp32a)

    print("(segment) division by background (numba)")
    divide(img_stack, tmp32a, keep, out=tmp32b)

    print("(segment) img3.memset(tmp32a, 0)")
    img3.memset(tmp32a, 0)

    print("(segment) denoise (img3.gauss)")
    img3.gauss(tmp32b, keep, sigmaD, denoised)


    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Exclusion of specific brain areas
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    excluded_brain_regions = ['Main olfactory bulb', 'Accessory olfactory bulb', 'Anterior olfactory nucleus', 'Taenia tecta', 'ventricular systems']
    excluded_area_IDs = ABAregion_to_ID(output_directory, excluded_brain_regions)
    print(excluded_area_IDs)

    print("(segment) Constructing a mask of excluded brain regions ...")
    tmp8[:,:,:] = 0
    for ID in excluded_area_IDs:
        print("   masking region:", ID)
        construct_mask(annotation_atlas, tmp8, ID)   # here tmp8 is the mask of all regions to be excluded

    print("(segment) Set to 0 excluded brain regions in denoised ...")
    remove_area(tmp8, denoised, 1)


    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Exclusion of atlas perimeter
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #

    print("(segment) tmp8=0 ...")
    tmp8[:,:,:] = 0
    print("(segment) Erode atlas perimeter ...")
    img3.erosion(keep, Nerosion, tmp8)

    print("(segment) Exclude eroded atlas perimeter ...")
    remove_area(tmp8, denoised, 0)


    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Segmentation
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    print("(segment) candidate cells from denoised (numba)")
    binary_value(denoised, keep, Imin)


    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Instance segmentation: Connected components
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    print("(segment) img3.labels")
    Nobjects = img3.labels(keep, labels, work); print("   Number of total objects:", Nobjects)

    print("(segment) img3.remove_small_objects")
    Nobjects = img3.remove_small_objects(labels, Vmin, work); print("   Number of accepted objects:", Nobjects)

    print("(segment) img3.objects")
    lst = img3.objects(labels, Nobjects)

    print("(segment) filter on Imax: loop over objects")
    lst1 = []
    for l in lst:
        Intensities = denoised[l[:,0], l[:,1], l[:,2]]
        if np.max(Intensities) >= Icmax:
            lst1.append(l)
    Nobjects = len(lst1); print("   Number of objects:", Nobjects)

    print("(segment) Saving object list in pickle ...")
    with open("%s/%s_lst.pkl" % (output_directory, os.path.basename(input_nrrd)),'wb') as fl:
        pickle.dump(lst1, fl)

