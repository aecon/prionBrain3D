from utils.dataset import Dataset
from utils.preprocessor import preprocess
from process.segmentation import segment
#from process import registration
#from process import quantification


# load setup file
dataset = Dataset("setup.yml")

# pre-process
preprocess(dataset)

# cell segmentation
segment(dataset)


## Registration
#data_registered = registration.process(input_data, output_dir, data_segmented)
#
#
## Quantification
#quantification.process(data_registered)


