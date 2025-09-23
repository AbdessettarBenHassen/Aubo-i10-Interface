#!/bin/bash

# ----------------------------
# Aubo-i10 Interface Launcher
# ----------------------------

# Activate the conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate py37

# Ensure robot library is visible
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)

# Run main.py (it will start the Python2 bridge itself)
python3 main.py



