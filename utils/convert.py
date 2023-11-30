import os
import img3


def tif2raw(tif_path, output_directory):

    # Output raw and nrrd paths
    odir = output_directory
    name = os.path.basename(tif_path)
    raw_path  = "%s/%s.raw"  % (odir, name)
    nrrd_path = "%s/%s.nrrd" % (odir, name)

    # Convert tif to raw/nrrd
    img3.tif2raw(tif_path, raw_path, nrrd_path, Verbose=False)

    return raw_path, nrrd_path

