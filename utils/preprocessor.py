import os
import sys
from utils.dataset import Dataset
from utils import convert
from utils import crop
from utils import flip
from utils.metadata import read_tiff_voxel_size
import img3


def preprocess(dataset):

    me = "preprocess"

    output_directory = dataset.output_directory


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Convert tif to raw/nrrd
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # convert signal channel tif to raw
    _raw, _nrrd = convert.get_filenames(dataset.input_tif, output_directory)
    if not os.path.isfile(_nrrd):
        print("(%s) Signal raw/nrrd does not exist. Generating now ..." % me)
        _, _ = convert.tif2raw(dataset.input_tif, output_directory)
    else:
        print("(%s) Signal raw/nrrd exist." % me)
    dataset.input_nrrd = _nrrd
    dataset.input_raw = _raw
        

    # convert autofluorescence channel tif to raw
    if dataset.input_autofluorescence_tif != None:
        _raw, _nrrd = convert.get_filenames(dataset.input_autofluorescence_tif, output_directory)
        if not os.path.isfile(_nrrd):
            print("(%s) Autofluorescence raw/nrrd does not exist. Generating now ..." % me)
            _, _ = convert.tif2raw(dataset.input_autofluorescence_tif, output_directory)
        else:
            print("(%s) Autofluorescence raw/nrrd exist." % me)
        dataset.input_autof_nrrd = _nrrd
        dataset.input_autof_raw  = _raw
    else:
        print("(%s) NO autofluorescence channel!" % me)


    # restore pixel sizes in nrrd files
    px, py, pz = dataset.pixel_sizes

    # signal channel
    #pz, py, px = read_tiff_voxel_size(dataset.input_tif)
    _dtype, _path, _shape, _offset, _dx, _dy, _dz = img3.nrrd_details(dataset.input_nrrd)
    img3.nrrd_write(dataset.input_nrrd, os.path.basename(_path), _dtype, _shape, (px,py,pz))

    # autofluorescence channel
    #pz, py, px = read_tiff_voxel_size(dataset.input_autofluorescence_tif)
    _dtype, _path, _shape, _offset, _dx, _dy, _dz = img3.nrrd_details(dataset.input_autof_nrrd)
    img3.nrrd_write(dataset.input_autof_nrrd, os.path.basename(_path), _dtype, _shape, (px,py,pz))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Crop
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if dataset.crop:

        _raw, _nrrd = crop.get_filenames(dataset.input_nrrd, output_directory)
        if not os.path.isfile(_nrrd):
            print("(%s) Cropping signal channel ..." % me)
            _, _ = crop.crop(dataset.input_nrrd, dataset.crop_coordinates, output_directory)
        else:
            print("(%s) Signal channel already cropped." % me)
        dataset.input_nrrd = _nrrd
        dataset.input_raw = _raw


        if dataset.input_autofluorescence_tif != None:
            _raw, _nrrd = crop.get_filenames(dataset.input_autof_nrrd, output_directory)
            if not os.path.isfile(_nrrd):
                print("(%s) Cropping autofluorescence channel ..." % me)
                _, _ = crop.crop(dataset.input_autof_nrrd, dataset.crop_coordinates, output_directory)
            else:
                print("(%s) Autofluorescence channel already cropped." % me)
            dataset.input_autof_nrrd = _nrrd
            dataset.input_autof_raw = _raw


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # flip
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if dataset.flip_horizontally:

        _raw, _nrrd = flip.get_filenames(dataset.input_nrrd, output_directory)
        if not os.path.isfile(_nrrd):
            print("(%s) Flipping (H) signal channel ..." % me)
            _, _ = flip.flip_horizontally(dataset.input_nrrd, output_directory)
        dataset.input_nrrd = _nrrd
        dataset.input_raw = _raw

        if dataset.input_autofluorescence_tif != None:
            _raw, _nrrd = flip.get_filenames(dataset.input_autof_nrrd, output_directory)
            if not os.path.isfile(_nrrd):
                print("(%s) Flipping (H) autofluorescence channel ..." % me)
                _, _ = flip.flip_horizontally(dataset.input_autof_nrrd, output_directory)
            dataset.input_autof_nrrd = _nrrd
            dataset.input_autof_raw = _raw
    else:
        print("(%s) NO horizontal flip." % me)


    if dataset.flip_stack:

        _raw, _nrrd = flip.get_filenames(dataset.input_nrrd, output_directory)
        if not os.path.isfile(_nrrd):
            print("(%s) Flipping (S) signal channel ..." % me)
            _, _ = flip.flip_stack(dataset.input_nrrd, output_directory)
        dataset.input_nrrd = _nrrd
        dataset.input_raw = _raw

        if dataset.input_autofluorescence_tif != None:
            _raw, _nrrd = flip.get_filenames(dataset.input_autof_nrrd, output_directory)
            if not os.path.isfile(_nrrd):
                print("(%s) Flipping (S) autofluorescence channel ..." % me)
                _, _ = flip.flip_stack(dataset.input_autof_nrrd, output_directory)
            dataset.input_autof_nrrd = _nrrd
            dataset.input_autof_raw = _raw
    else:
        print("(%s) NO stack flip." % me)

