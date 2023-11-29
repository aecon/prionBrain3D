#!/bin/bash

ELASTIX_PATH=/home/neptun/Downloads/elastix
export LD_LIBRARY_PATH=${ELASTIX_PATH}/lib/
elastix="${ELASTIX_PATH}/bin/elastix"

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

out=$1
input=$2

atlas=${SCRIPTPATH}/"fixed.mhd"
affine=${SCRIPTPATH}/"affine.txt"
mkdir -p ${out}

${elastix} -out ${out} -f ${atlas} -m ${input} -p ${affine} -threads 64

