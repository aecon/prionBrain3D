import os
import nrrd
import skimage.io
import numpy as np
from pathlib import Path
from allensdk.core.reference_space_cache import ReferenceSpaceCache


def ABAregion_to_ID(odir, brain_regions, resolution=25):

    print("(generate_region_mask) Downloading atlas...")
    reference_space_key = os.path.join('annotation', 'ccf_2017')

    # Load Reference Space
    rspc = ReferenceSpaceCache(resolution, reference_space_key, manifest=Path(odir) / 'manifest.json')
    tree = rspc.get_structure_tree(structure_graph_id=1) 

    # Get brain region IDs
    print("(generate_region_mask) Retrieving region IDs...")
    main_brain_region_IDs = []
    for _region in brain_regions:
    	_structure = tree.get_structures_by_name([_region])
    	main_brain_region_IDs.append(_structure[0]['id'])

    return main_brain_region_IDs
 
