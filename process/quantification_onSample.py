import os
import nrrd
import skimage.io
import numpy as np

import img3
from process.numba_functions import *
from process.ABA_regions import ABAregion_to_ID
from utils.dataset import Dataset


def quantify(dataset):

    output_directory = dataset.output_directory

    # Load aligned segmented data (treated as a binary mask)
    f_segmented_nrrd = dataset.segmented_nrrd
    print("(quantify) Loading segmented cells")
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(denoised_nrrd)
    denoised = np.memmap(path, dtype, 'r', offset=offset, shape=shape, order='F')

    # Load aligned annotation atlas
    f_aligned_annotated_atlas = dataset.registered_annotation_atlas
    print("(quantify) Loading transformed annotation atlas")
    annotation_atlas, _ = nrrd.read(f_aligned_annotated_atlas)

    # IDs of quantification regions
    odir_tmp = output_directory + "/tmp"
    if not os.path.exists(odir_tmp):
        os.makedirs(odir_tmp)

    brain_regions = ['Hippocampal formation', 'Isocortex', 'Thalamus', 'Hypothalamus', 'Cerebellum', 'Brain stem']
    print("(quantify) get quantification area IDs")
    area_IDs = ABAregion_to_ID(odir_tmp, brain_regions)
    print(area_IDs)

    # Volume of detected cells per brain region
    mask = img3.mmap_create("%s/tmp_mask.raw" % odir_tmp, np.dtype("uint8"), shape)

    print("(quantify) setting mask elements to 0")
    mask[:,:,:] = 0

    cell_volume_per_region = []
    volume_per_region = []
    for ID in area_IDs:

        construct_mask(annotation_atlas, mask, ID)

    	# Mask: detected cells inside brain region
    	_cells_inside_mask = np.zeros(np.shape(data))
    	idx = (data>0)*(_mask>0)
    	_cells_inside_mask[idx] = 1

    	# Total cell volume in region
    	_volume = np.sum(_cells_inside_mask)
    	cell_volume_per_region.append(_volume)

    	# Volume of brain region
    	volume_per_region.append(np.sum(_mask))


    # Write statistics to file
    with open('%s/%s_stats_volume_per_region.dat' % (output_directory, os.path.basename(f_segmented_nrrd)), 'w') as f:

    	# header
    	f.write("%25s " % "QUANTITY")
    	for region in brain_regions:
    		f.write("%20s " % region)
    	f.write("\n")

    	# row 1: region volumes
    	f.write("%25s " % "Region volume (mm^3):")
    	for volume in volume_per_region:
    		f.write( "%20.2f " % (volume * pow(resolution*1.e-3, 3)) )
    	f.write("\n")

    	# row 2: cell volumes
    	f.write("%25s " % "% Vcell/Vregion (mm^3):")
    	for cell_volume, volume in zip(cell_volume_per_region, volume_per_region):
    		f.write( "%20.2f " % (cell_volume/volume * 100.) )
    	f.write("\n")

