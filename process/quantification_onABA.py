# Reference     : https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#making-structure-masks

import os
import skimage.io
import numpy as np
from pathlib import Path
from allensdk.core.reference_space_cache import ReferenceSpaceCache


# TODO: Update function name and input arguments to match main.py !

def process(aligned_mask):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # User settings
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Screen output
    verbose = False
    is_half_brain = True
    
    # Paths
    output_dir = 'out'
    #aligned_mask = 'data/test_segmented_mask.tif'
    
    # Atlas
    resolution = 25
    reference_space_key = os.path.join('annotation', 'ccf_2017')
    
    # Brain regions (using ABA nomenclature)
    # see http://atlas.brain-map.org/atlas?atlas=2
    brain_regions = ['Hippocampal formation', 'Isocortex', 'Thalamus', 'Hypothalamus', 'Cerebellum', 'Brain stem']
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Mask generation per brain region
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # Load Reference Space
    rspc = ReferenceSpaceCache(resolution, reference_space_key, manifest=Path(output_dir) / 'manifest.json')
    tree = rspc.get_structure_tree(structure_graph_id=1) 
    
    # Get brain region IDs
    main_brain_region_IDs = []
    for _region in brain_regions:
    	_structure = tree.get_structures_by_name([_region])
    	if verbose:
    		print('\n', _structure)
    	main_brain_region_IDs.append(_structure[0]['id'])
    if verbose:
    	print('\nMain brain region IDs:', main_brain_region_IDs)
    
    # Download annotation volume
    annotation, meta = rspc.get_annotation_volume()
    
    # Construct ReferenceSpace
    rsp = rspc.get_reference_space()
    
    # Remove unassigned structures
    rsp.remove_unassigned()
    
    # Generate mask for each brain region
    all_masks = []
    for _id in main_brain_region_IDs:
    	_mask = rsp.make_structure_mask([_id])
    	all_masks.append(_mask)
    
    # Reorient masks to saggital ABA view
    reshaped_masks = []
    for _mask in all_masks:
    	Nx, Ny, Nz = np.shape(_mask)   #(528, 320, 456
    	if is_half_brain==True:
    		Nz = Nz//2
    	_tmp = np.zeros((Ny, Nx, Nz))
    	for k in range(Nz):
    		_tmp[:,:,k] = (_mask[:,:,k]).T
    	reshaped_masks.append(_tmp)
    
    # Save masks as tif files
    for _mask, _region in zip(reshaped_masks, brain_regions):
    	skimage.io.imsave("%s/mask_%s.tif" % (output_dir, _region), _mask.T, plugin="tifffile", check_contrast=False)
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Statistics
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # Load aligned segmented data (treated as a binary mask)
    data = skimage.io.imread(aligned_mask).T
    
    # Volume of detected cells per brain region
    cell_volume_per_region = []
    volume_per_region = []
    for _mask in reshaped_masks:
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
    with open('%s/stats_volume_per_region.dat' % output_dir, 'w') as f:
    
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
    	f.write("%25s " % "Cell volume (mm^3):")
    	for cell_volume in cell_volume_per_region:
    		f.write( "%20.2f " % (cell_volume * pow(resolution*1.e-3, 3)) )
    	f.write("\n")
    

