import os
from utils import yaml_reader


class Dataset:

    def __init__(self, name, dictionary):

        self.name = name

        # directories
        self.input_autofluorescence_tif = dictionary["input_autofluorescence"]
        self.input_tif = dictionary["input_data"]
        self.output_directory = "%s/out" % os.path.dirname(self.input_tif)
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        # pixel size in micro-meters
        self.pixel_sizes = dictionary["spacings"]

        # inputs: signal channel
        self.input_nrrd = None
        self.input_raw = None

        # inputs: autofluorescence channel
        self.input_autof_nrrd = None
        self.input_autof_raw = None

        # preprocessing
        self.flip_horizontally = dictionary["flip_horizontally"]   # 0/1 flip horizontally?
        self.flip_stack = dictionary["flip_stack"]   # 0/1 flip stack?
        self.crop = dictionary["crop"]   # 0/1 crop?
        self.crop_coordinates = dictionary["crop_coordinates"]   # [x0,y0,x1,y1]

        # registration
        self.registered_reference_atlas = None
        self.registered_annotation_atlas = None

        # segmentation
        self.denoised_nrrd = None
        self.lst_pickle = None

        # classification
        self.features = None
        self.segmented_nrrd = None



class DataCollection:

    def __init__(self, setup_file):

        self.datasets = []

        dictionary = yaml_reader.load(setup_file)
        for k in dictionary.keys():
            y = dictionary[k]

            data = Dataset(k, y)
            self.datasets.append(data)


