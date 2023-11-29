from utils import yaml_reader

class Dataset:

    def __init__(self, setup_file):

        y = yaml_reader.load(setup_file)
        print(y)

        # paths
        self.input_tif = y["database"]["input_data"]
        self.output_directory = y["database"]["output_directory"]
        self.input_nrrd = None
        self.input_raw = None

        # preprocessing
        self.flipH = y["database"]["flip_horizontally"]   # flip horizontally
        self.flipS = y["database"]["flip_horizontally"]   # flip stack
        self.crop = y["database"]["crop"]  # True/False whether to crop
        self.crop_coordinates = y["database"]["crop_coordinates"]   # [x0,y0,x1,y1]

        # segmentation
        self.segmented_nrrd = None

        # registration
        self.registered_mhd = None


