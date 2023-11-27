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
# SAMPLES AND CORRESPONDING INTENSITIES
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
samples=("sample1" "sample2" "sample3" "sample4")

for sample in ${samples[@]}; do

    input=`find "${DATA}/cropped_647" -name "cropped_raw_${sample}*.nrrd"`
    ls $input

    outdir="${OUTDIR}/${sample}"
    mkdir -p "${outdir}"

    Imin=300
    Imax=2000
    echo $sample $Imin $Imax

    python3 segmentation -i "${input}" -o "${outdir}" -Imin $Imin -Imax $Imax -v -p

    # remove intermediate files
    rm "${outdir}"/segment/mask.raw
    rm "${outdir}"/segment/mask_erosion.raw
    rm "${outdir}"/segment/tmp8.raw
    rm "${outdir}"/segment/tmp32a.raw
    rm "${outdir}"/segment/tmp32b.raw
    rm "${outdir}"/segment/labels.raw
    rm "${outdir}"/segment/work.raw
    rm "${outdir}"/segment/denoised.raw

done

