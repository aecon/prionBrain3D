#!/bin/bash
set -eu

#
# Registration of atlas onto the autofluorescence channel
# retult: a transformed atlas file to match the autof. channel
#

if [ "$#" -ne 2 ]; then
    echo "run_elastix_atlas2autof.sh requires 2 input arguments:"
    echo "./run_elastix_atlas2autof.sh <OUTPUT DIRECTORY> <AUTOFLUORESCENCE CHANNEL>"
    exit
fi

ELASTIX_PATH=${HOME}/Downloads/elastix
export LD_LIBRARY_PATH=${ELASTIX_PATH}/lib/
elastix="${ELASTIX_PATH}/bin/elastix"
transformix="${ELASTIX_PATH}/bin/transformix"

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

out=$1
input_auto=$2
echo $out
echo $input_auto


atlas=${SCRIPTPATH}/"ABA_25um_reference_hemisphere.nrrd"
atlas_annotation=${SCRIPTPATH}/"ABA_25um_annotation_hemisphere.nrrd"
affine=${SCRIPTPATH}/"affine.txt"
bspline=${SCRIPTPATH}/"bspline.txt"
threads=32

outEa=${out}/elastix_affine
outEb=${out}/elastix_bspline
outT=${out}/transformix
mkdir -p ${outEa}
mkdir -p ${outEb}
mkdir -p ${outT}

# registration of atlas onto the autofluorescence channel
if [ ! -f "${outEa}/result.0.nrrd" ]; then
    ${elastix} -out ${outEa} -m ${atlas} -f ${input_auto} -p ${affine} -threads $threads
fi
if [ ! -f "${outEb}/result.0.nrrd" ]; then
    ${elastix} -out ${outEb} -m ${atlas} -f ${input_auto} -p ${bspline} -t0 ${outEa}/TransformParameters.0.txt  -threads $threads
fi

# transformation of annotation atlas 
# edit the Bspline file to use for transforming binary segmented data
if [ ! -f "${outT}/result.nrrd" ]; then
    cp ${outEb}/TransformParameters.0.txt ${outT}/
    sed -i "/FinalBSplineInterpolationOrder/c\(FinalBSplineInterpolationOrder 0)" ${outT}/TransformParameters.0.txt
    
    # apply transformation to segmentation
    ${transformix} -in ${atlas_annotation} -out ${outT} -tp ${outT}/TransformParameters.0.txt -threads $threads
fi

