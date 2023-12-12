# prionBrain3D

**Under Development. The corresponding publication will be available soon.**

A python package to analyze 3D neuronal cells in prion-infected brain samples, acquired at micro-meter pixel resolution.


## Requirements

* [img3D package](https://github.com/aecon/img3D)
* [elastix](https://elastix.lumc.nl)
* [Fiji](https://fiji.sc)
* [AllenSDK](https://allensdk.readthedocs.io/en/latest)
* Python packages (see below)


### Installation

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
-->

