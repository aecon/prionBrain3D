from utils.dataset import Dataset
from utils.convert import tif2raw
from utils.crop import crop


def preprocess(dataset):

    # convert tif to raw
    _raw, _nrrd = tif2raw(dataset.input_tif)
    dataset.input_nrrd = _nrrd
    dataset.input_raw = _raw

    # crop
    _raw, _nrrd = crop(dataset.input_nrrd, dataset.crop_coordinates)
    dataset.input_nrrd = _nrrd
    dataset.input_raw = _raw


    # flip
    # TODO ...



