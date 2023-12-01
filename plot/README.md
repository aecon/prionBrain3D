# Plots


## Contents


### voxelization

Returns a smoother version of the aligned `transformed_cells.nrrd`.

```        
python voxelization.py -i "${input}"
```


### Coronal slices of cell density

Generates a montage of coronal slices with voxelized cell density.

```
python coronal_per_sample.py -i $VOXELIZED_CELLS -o $OUTPUT_DIRECTORY -s $SAMPLE_ID
```


### Average cell density

Averages the cell density between all samples in a cohort.

```
python plot_avg_density.py -i $LIST_OF_ALIGNED_FILES_IN_COHORT -on "blur" -o $OUTPUT_DIRECTORY -g 2 -of $FIGURE_NAME
```


### Spatial statistical significance

Generates a 3D pvalue map, between control and treated groups.

```
python plot_pvalue_overlay_to_saline.py  -f1 $AVG_GROUP2.nrrd -f2 $AVG_GROUP1.nrrd 
                                         -f1s $STD_GROUP2.nrrd -f2s $STD_GROUP1.nrrd \
                                         -g 2 -o $OUTPUT_DIRECTORY -R $SMOOTHING_RADIUS
```


### Cluster correction

Performs Bonferroni correction on the pvalue maps.

```
python3.8 cluster_correct.py -p $PVALUE_MAP.nrrd
```

