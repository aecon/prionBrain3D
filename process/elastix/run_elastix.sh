#!/bin/bash
set -eu

if [ "$#" -ne 3 ]; then
    echo "run_elastix.sh requires 3 input arguments"
    exit
fi

ELASTIX_PATH=/home/neptun/Downloads/elastix
export LD_LIBRARY_PATH=${ELASTIX_PATH}/lib/
elastix="${ELASTIX_PATH}/bin/elastix"
transformix="${ELASTIX_PATH}/bin/transformix"

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

out=$1
input_auto=$2
input_seg=$3
echo $out
echo $input_auto
echo $input_seg


atlas=${SCRIPTPATH}/"atlas.nrrd"
affine=${SCRIPTPATH}/"affine.txt"
bspline=${SCRIPTPATH}/"bspline.txt"
threads=32

outEa=${out}/elastix_affine
outEb=${out}/elastix_bspline
outT=${out}/transformix
mkdir -p ${outEa}
mkdir -p ${outEb}
mkdir -p ${outT}

# autofluorescence registration
${elastix} -out ${outEa} -f ${atlas} -m ${input_auto} -p ${affine} -threads $threads
${elastix} -out ${outEb} -f ${atlas} -m ${input_auto} -p ${bspline} -t0 ${outEa}/TransformParameters.0.txt  -threads $threads

# append to Bspline file
echo "(FinalBSplineInterpolationOrder 0)" >> ${outEb}/TransformParameters.0.txt

# apply transformation to segmentation
${transformix} -in ${input_seg} -out ${outT} -tp ${outEb}/TransformParameters.0.txt -threads $threads

