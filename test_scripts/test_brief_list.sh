#!/bin/bash

# Dynamically determine the project root and src directory
SCRIPT_DIR=$(dirname "$0")
SRC_DIR="$SCRIPT_DIR/../src"

# Set PYTHONPATH to both src and site-packages
export PYTHONPATH="$SRC_DIR:/usr/local/lib/python3.9/site-packages"

# Define Input and Output Paths
INPUT_CSV="/home.zfs/wustl/kadic/txt_files/input/projects.txt"
OUTPUT_FILE="/home.zfs/wustl/kadic/txt_files/output/projects_list.txt"

# Run the Python script for the brief list
python3 -m xnat_cli_scripts.projects --L --brief --csv "$INPUT_CSV" > "$OUTPUT_FILE"

# Check if the output file was created and display a success message
if [[ -f "$OUTPUT_FILE" ]]; then
    echo "Brief list output saved to $OUTPUT_FILE"
else
    echo "[ERROR] Failed to generate brief list output."
fi
