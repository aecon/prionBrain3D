import os
import sys
import nrrd
import pickle
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


    # List of all necessary outputs of this function
    # - denoised:
    f_denoised_nrrd = "%s/%s_denoised.nrrd" % (output_directory, os.path.basename(input_nrrd))
    f_denoised_raw  = "%s/%s_denoised.raw"  % (output_directory, os.path.basename(input_nrrd))
    dataset.denoised_nrrd = f_denoised_nrrd
    # - objects:
    f_lst = "%s/%s_lst.pkl" % (output_directory, os.path.basename(input_nrrd))
    dataset.lst_pickle = f_lst


    if (not os.path.exists(f_denoised_nrrd)) or (not os.path.exists(f_lst)):

        dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(input_nrrd)

        #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Generate temporary work arrays
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        print("(segment) creating work arrays ...")

        odir_tmp = output_directory + "/tmp"
        if not os.path.exists(odir_tmp):
            os.makedirs(odir_tmp)

        f_tmp8 = "%s/tmp_8.raw"         % odir_tmp
        f_keep = "%s/tmp_mask.raw"      % odir_tmp
        f_tmp32a = "%s/tmp_32a.raw"     % odir_tmp
        f_tmp32b = "%s/tmp_32b.raw"     % odir_tmp
        f_labels = "%s/tmp_labels.raw"  % odir_tmp
        f_work   = "%s/tmp_work.raw"    % odir_tmp

        tmp8 = img3.mmap_create(f_tmp8, np.dtype("uint8"), shape)
        keep = img3.mmap_create(f_keep, np.dtype("uint8"), shape)
        tmp32a  = img3.mmap_create(f_tmp32a, np.dtype("float32"), shape)
        tmp32b  = img3.mmap_create(f_tmp32b, np.dtype("float32"), shape)
        labels  = img3.mmap_create(f_labels, np.dtype(np.int64), shape)
        work    = img3.mmap_create(f_work, np.dtype(np.int64), shape)

        denoised = []
        if not os.path.isfile(f_denoised_nrrd):
            denoised = img3.mmap_create(f_denoised_raw, np.dtype("float32"), shape)

            #
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Exclusion of specific brain areas
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #
            print("(segment) Loading transformed annotation atlas")
            annotation_atlas, _ = nrrd.read(annotation_atlas_nrrd)

            # full sample mask
            print("(segment) make full sample mask")
            construct_mask_0(annotation_atlas, keep, 0)

            excluded_brain_regions = ['Main olfactory bulb', 'Accessory olfactory bulb', 'Anterior olfactory nucleus', 'Taenia tecta', 'ventricular systems']
            excluded_area_IDs = ABAregion_to_ID(odir_tmp, excluded_brain_regions)
            excluded_area_IDs.append(81) # the big empty triangular hole
            print("(segment) excluded region IDs:", excluded_area_IDs)

            # exclude regions from sample mask
            print("(segment) remove excluded brain regions from sample mask ...")
            for ID in excluded_area_IDs:
                print("   masking region:", ID)
                construct_mask(annotation_atlas, keep, ID)


            # erosion of atlas perimeter
            print("(segment) set tmp8 to 0 ...")
            tmp8[:,:,:] = 0

            print("(segment) erode atlas perimeter ...")
            img3.erosion(keep, Nerosion, tmp8)

            print("(segment) keep <- tmp8 ...")
            keep[:,:,:] = tmp8[:,:,:]


            #
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Normalization and Denoise
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #
            print("(segment) Loading input data ...")
            dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(input_nrrd)
            img_stack = img3.read_input(input_nrrd, path, dtype, offset, shape)

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

            img3.nrrd_write(f_denoised_nrrd, f_denoised_raw, np.dtype("float32"), shape, spacings)

        else:
            _dtype, _path, _shape, _offset, dx, dy, dz = nrrd_details(f_denoised_nrrd)
            denoised = img3.read_input(f_denoised_nrrd, _path, _dtype, _offset, _shape)


        #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Segmentation
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        print("(segment) candidate cells from denoised (numba)")
        binary_value(denoised, keep, Imin)  # overwriting keep to store segmented data


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
        with open(f_lst,'wb') as fl:
            pickle.dump(lst1, fl)

    else:
        print("(segment) Segmentation completed.")

