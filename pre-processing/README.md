# Image pre-processing


## Cropping

Crop image data to contain only regions of interest. Useful to exclude large empty spaces generated with automated tiling in light-sheet microscopy.
```
./run_crop.sh
```
The upper left and bottom right corners for each sample are stored inside the file
```
corners.dat
```


## Flipping

Used to flip samples such that cerebellum is on the Left. Useful for further registration to the Allen Brain Anatomical Atlas.
```
python3 flip.py -i <path to nrrd file>
```


