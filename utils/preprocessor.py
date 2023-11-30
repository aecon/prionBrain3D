import os
from utils.dataset import Dataset
from utils.convert import tif2raw
from utils.crop import crop
from utils.flip import flip_horizontally, flip_stack
from utils.metadata import read_tiff_voxel_size
import img3


def preprocess(dataset):

    output_directory = dataset.output_directory

    # convert tif to raw
    _raw, _nrrd = tif2raw(dataset.input_tif, output_directory)
    dataset.input_nrrd = _nrrd
    dataset.input_raw = _raw

    # restore pixel size metadata
    pz, py, px = read_tiff_voxel_size(dataset.input_tif)
    _dtype, _path, _shape, _offset, _dx, _dy, _dz = img3.nrrd_details(dataset.input_nrrd)
    img3.nrrd_write(dataset.input_nrrd, os.path.basename(_path), _dtype, _shape, (px,py,pz))

    # crop
    if dataset.crop:
        _raw, _nrrd = crop(dataset.input_nrrd, dataset.crop_coordinates, output_directory)
        dataset.input_nrrd = _nrrd
        dataset.input_raw = _raw

    # flip
    if dataset.flip_horizontally:
        _raw, _nrrd = flip_horizontally(dataset.input_nrrd, output_directory)
        dataset.input_nrrd = _nrrd
        dataset.input_raw = _raw

    if dataset.flip_stack:
        _raw, _nrrd = flip_stack(dataset.input_nrrd, output_directory)
        dataset.input_nrrd = _nrrd
        dataset.input_raw = _raw

