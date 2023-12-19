import sys
from utils.dataset import Dataset, DataCollection
from utils.preprocessor import preprocess
from process.segmentation_test import segment
from process.registration import register_atlas2autofluorescence as register
from process.classification import classify
from process.quantification_onSample import quantify


collection = DataCollection("setup_testSert.yml")

for dataset in collection.datasets:

    # pre-process
    stop_for_cropping = preprocess(dataset)
    if stop_for_cropping==True:
        print("(main) Stopped for cropping.")
        print("(main) Use ImageJ to find crop coordinates, store them inside the setup file and rerun.")
        continue
    else:
        print("(main) Continuing with rest of processing ...")

    # registration
    register(dataset)

    # cell segmentation
    segment(dataset)

    # classification
    classify(dataset)

    # quantification
    quantify(dataset)

