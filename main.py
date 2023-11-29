from utils.dataset import Dataset
from utils.preprocessor import preprocess
from process.segmentation import segment
from process.registration import register
#from process import quantification


# load setup file
dataset = Dataset("setup.yml")

# pre-process
preprocess(dataset)

# cell segmentation
segment(dataset)

# registration
register(dataset)


## Quantification
#quantification.process(data_registered)


