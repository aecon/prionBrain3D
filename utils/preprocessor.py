from utils.dataset import Dataset
from utils.convert import tif2raw
from utils.crop import crop
from utils.flip import flip_horizontally, flip_stack


def preprocess(dataset):

    output_directory = dataset.output_directory

    # convert tif to raw
    _raw, _nrrd = tif2raw(dataset.input_tif, output_directory)
    dataset.input_nrrd = _nrrd
    dataset.input_raw = _raw

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

