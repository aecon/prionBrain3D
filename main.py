import sys
from utils.dataset import Dataset, DataCollection
from utils.preprocessor import preprocess
from process.segmentation import segment
from process.registration import register
from process.classification import classify
#from process import quantification


# load setup file
collection = DataCollection("setup.yml")

# loop over samples in collection
for dataset in collection.datasets:

    # pre-process
    preprocess(dataset)

    # cell segmentation
    segment(dataset)

    # classification
    classify(dataset)

    # registration
    #register(dataset)

    # quantification
    #quantification.process(data_registered)


