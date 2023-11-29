#!/bin/bash
set -eu


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DATA PATHS
# - DATA: Folder containing input data
# - OUTDIR: Folder to store output
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DATA="./brains"
OUTDIR="./brains/output"


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAMPLES
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
samples=("sample1" "sample2" "sample3" "sample4")

for sample in ${samples[@]}; do
    echo "SAMPLE: ${sample}"

    # USE AUTOFLUORESCENCE CHANNEL FOR REGISTRATION (520)
    input=`find "${DATA}/cropped_520" -name "cropped_raw_${sample}*.nrrd"`
    echo "BRAIN:"; ls ${input}

    # SIGNAL CHANNEL (647)
    truecells="${OUTDIR}/cropped_647/${sample}/segmented.nrrd"
    echo "CELLS:"; ls ${truecells}

    outdir="${OUTDIR}/${sample}/align"
    mkdir -p "${outdir}"

    # side of Cerebellum: ALWAYS on the LEFT: -1
    ox=-1

    python3.6 registration.py -i ${input} -o ${outdir} -k 1 1 1 -d 3.26 3.26 3.00 -azmin 0 -azmax 230 -ori $ox 2 3 -N 32 -truecells ${truecells} -affine affine.txt -bspline bspline.txt -v

    # Remove temporary file
    rm -rf ${outdir}/stitched.npy

done

