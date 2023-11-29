#from process import segmentation
#from process import registration
#from process import quantification
from utils.dataset import Dataset
from utils.preprocessor import preprocess


# load setup file
dataset = Dataset("setup.yml")

# pre-process
preprocess(dataset)


#
## Load configuration file
#C = DataLoader("configuration.yml")
#input_data = C.dict["input"]
#output_dir = C.dict["output"]
#
#
## Segmentation
#data_segmented = segmentation.process(input_data, output_dir)
#
#
## Registration
#data_registered = registration.process(input_data, output_dir, data_segmented)
#
#
## Quantification
#quantification.process(data_registered)


