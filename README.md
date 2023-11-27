# prionBrain3D

**CAUTION: WORK IN PROGRESS!**

Under development is a python toolkit for image processing of large, three-dimensional whole mouse brains.



## Requirements

* C compiler
* numpy
* [img3D package](https://github.com/aecon/img3D)

### Optional requirements

* C compiler with OpenMP support
* ImageJ
* Python packages: tifffile, numba, scipy, scikit-image, pandas, matplotlib




## Contents

* pre-processing: Data cropping and flipping.

* segmentation: Segmentation of neuronal cells.

* registration: Registration of brain data to the Allen Brain Anatomical Atlas.

* quantification: Regional statistics for total cell volume.



## Data

3D image files obtained from Light-sheet microscopy.

### Location

The location of the data should be stored in the environment variable `${DATA}`.


