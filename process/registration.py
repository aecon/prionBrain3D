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


def register_autofluorescnec_signal(dataset):

    output_directory = dataset.output_directory

    autofluorescence_nrrd = dataset.input_autof_nrrd
    signal_nrrd = dataset.input_nrrd

    autofluorescence_nrrd_big_endian = dataset.input_autof_nrrd + "IJ.nrrd"
    signal_nrrd_big_endian = dataset.input_nrrd + "IJ.nrrd"

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

    # - signal
    if not os.path.isfile(signal_nrrd_big_endian):
        cmd = "%s --headless -macro process/imagej/save_nrrd.ijm %s,%s" % (imageJpath, (signal_nrrd), (signal_nrrd_big_endian))
        print("(registration) Converting signal channel to big endian ...")
        os.system(cmd)
    else:
        print("(registration) Signal channel (big endian) exists:")
        print(signal_nrrd_big_endian)


    # run elstix for brain registration to Allen Brain Anatomical Atlas
#    cmd = "./process/elastix/run_elastix.sh %s %s %s" % (output_directory, autofluorescence_nrrd_big_endian, signal_nrrd_big_endian)
#    os.system(cmd)

