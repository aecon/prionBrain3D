import os
import sys

import img3
from utils.dataset import Dataset


def register(dataset):

    output_directory = dataset.output_directory
    autofluorescence_nrrd = dataset.input_nrrd
    segmented_nrrd = dataset.segmented_nrrd
    segmented_nrrd_big_endian = dataset.segmented_nrrd + "IJ.nrrd"
    autofluorescence_nrrd_big_endian = dataset.input_nrrd + "IJ.nrrd"

    # generate nrrd input for elastic in big endian order
    imageJpath = "/home/neptun/Desktop/Fiji_AE.app/ImageJ-linux64"
    basedir = os.path.abspath(os.getcwd())

    # - autofluorescence
    cmd = "%s --headless -macro process/imagej/save_nrrd.ijm %s,%s" % (imageJpath, (basedir+"/"+autofluorescence_nrrd), (basedir+"/"+autofluorescence_nrrd_big_endian))
    os.system(cmd)

    # - segmented
    cmd = "%s --headless -macro process/imagej/save_nrrd.ijm %s,%s" % (imageJpath, (basedir+"/"+segmented_nrrd), (basedir+"/"+segmented_nrrd_big_endian))
    os.system(cmd)

    # run elstix for brain registration to Allen Brain Anatomical Atlas
    cmd = "./process/elastix/run_elastix.sh %s %s %s" % (output_directory, autofluorescence_nrrd_big_endian, segmented_nrrd_big_endian)
    os.system(cmd)

