# prionBrain3D

A codebase for image processing of large 3D image stacks of whole mouse-brains.  


## Requirements

* [img3D package](https://github.com/aecon/img3D)
* [elastix](https://elastix.lumc.nl)
* [Fiji](https://fiji.sc)
* [AllenSDK](https://allensdk.readthedocs.io/en/latest)
* Python packages (see below)


## Installation

Create a new conda environment.
```
conda create -n "prionBrain3D" python=3.10.13
```

Activate the environment.
```
conda activate prionBrain3D
```

Install python packages.
```
pip install -r requirements.txt
```

<!---
I installed:
    conda install scikit-learn scikit-image pyparsing six pyyaml statsmodels
    pip install allensdk
    pip install ipykernel
    python -m ipykernel install --user --name=prionBrain3D
-->


## Authors
Developed by Athena Economides. The corresponding publication is **in preparation**.

Athena Economides, PhD  
Lab of Prof. Adriano Aguzzi  
Institute of Neuropathology  
University of Zurich  
Schmelzbergstrasse 12  
CH-8091 Zurich  
Switzerland

