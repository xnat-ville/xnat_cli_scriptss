#!/bin/bash

# Set PYTHONPATH to source code only (relative to the script's location)
export PYTHONPATH="$1/../src"

# Define Paths
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
