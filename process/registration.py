import os
import sys

import img3
from utils.dataset import Dataset


def register(dataset):

    input_file = dataset.input_nrrd
    output_directory = dataset.output_directory
    segmented_nrrd = dataset.segmented_nrrd

    os.system("pwd")

    cmd = "./process/elastix/run_elastix.sh %s %s" % (output_directory, input_file)
    os.system(cmd)


