import os
import img3


def get_filenames(tif_path, output_directory):
    """
    Returns paths to the generated raw and nrrd files
    """
    odir = output_directory
    name = os.path.basename(tif_path)
    raw_path  = "%s/%s.raw"  % (odir, name)
    nrrd_path = "%s/%s.nrrd" % (odir, name)
    return raw_path, nrrd_path


def tif2raw(tif_path, output_directory):
    """
    Converts the tif image into:
    - a raw file containing the data
    - an nrrd file containing image metadata
    """
    raw_path, nrrd_path = get_filenames(tif_path, output_directory)
    img3.tif2raw(tif_path, raw_path, nrrd_path, Verbose=False)
    return raw_path, nrrd_path

