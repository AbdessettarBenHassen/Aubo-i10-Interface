#!/bin/bash
# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate py37

# Navigate to project folder
cd /root/桌面/Aubo/Aubo-i10-Interface

# Kill any process using port 5000 (ignore errors)
fuser -k 5000/tcp 2>/dev/null || true

# Run the main Python app
python3 main.py

