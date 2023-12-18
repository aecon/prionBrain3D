import os
import sys

import img3
from utils.dataset import Dataset


def register_signal_segmented(dataset):

    output_directory = dataset.output_directory

    autofluorescence_nrrd = dataset.input_nrrd
    segmented_nrrd = dataset.segmented_nrrd

    segmented_nrrd_big_endian = dataset.segmented_nrrd + "IJ.nrrd"
    autofluorescence_nrrd_big_endian = dataset.input_nrrd + "IJ.nrrd"

    # generate nrrd input for elastic in big endian order
    imageJpath = "/home/neptun/Desktop/Fiji_AE.app/ImageJ-linux64"
    basedir = os.path.abspath(os.getcwd())

    # - autofluorescence
    cmd = "%s --headless -macro process/imagej/save_nrrd.ijm %s,%s" % (imageJpath, (autofluorescence_nrrd), (autofluorescence_nrrd_big_endian))
    os.system(cmd)

    # - segmented
    cmd = "%s --headless -macro process/imagej/save_nrrd.ijm %s,%s" % (imageJpath, (segmented_nrrd), (segmented_nrrd_big_endian))
    os.system(cmd)

    # run elstix for brain registration to Allen Brain Anatomical Atlas
    cmd = "./process/elastix/run_elastix.sh %s %s %s" % (output_directory, autofluorescence_nrrd_big_endian, segmented_nrrd_big_endian)
    os.system(cmd)


def register_atlas2autofluorescence(dataset):

    output_directory = dataset.output_directory

    autofluorescence_nrrd = dataset.input_autof_nrrd
    autofluorescence_nrrd_big_endian = dataset.input_autof_nrrd + "IJ.nrrd"

    # generate nrrd input for elastic in big endian order
    imageJpath = "/home/neptun/Desktop/Fiji_AE.app/ImageJ-linux64"
    basedir = os.path.abspath(os.getcwd())

    # - autofluorescence
    if not os.path.isfile(autofluorescence_nrrd_big_endian):
        cmd = "%s --headless -macro process/imagej/save_nrrd.ijm %s,%s" % (imageJpath, (autofluorescence_nrrd), (autofluorescence_nrrd_big_endian))
        print("(registration) Converting autofluorescence channel to big endian ...")
        os.system(cmd)
    else:
        print("(registration) Autofluorescence channel (big endian) exists:")
        print(autofluorescence_nrrd_big_endian)

    # output filenames after registration
    dataset.registered_reference_atlas = "%s/elastix_bspline/result.0.nrrd" % (output_directory)
    dataset.registered_annotation_atlas = "%s/transformix/result.nrrd" % (output_directory)

    # run elstix for brain registration to Allen Brain Anatomical Atlas
    if ( not os.path.isfile(dataset.registered_reference_atlas) ) or ( not os.path.isfile(dataset.registered_annotation_atlas) ):
        print("(registration) Running elastix ...")
        cmd = "./process/elastix/run_elastix_atlas2autof.sh %s %s" % (output_directory, autofluorescence_nrrd_big_endian)
        os.system(cmd)
    else:
        print("(registration) Registration completed.")
