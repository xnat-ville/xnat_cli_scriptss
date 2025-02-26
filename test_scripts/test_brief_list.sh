#!/bin/bash

# Function to list projects in brief format
# Arguments:
#   $1 - Base Folder (to set PYTHONPATH)
#   $2 - Boiler Plate arguments
#   $3 - CSV Input File
#   $4 - Output File
list_projects_brief() {
    # Dynamically set PYTHONPATH relative to the base folder
    export PYTHONPATH="$1/../src"

    echo "Running brief list"
    python3 -m xnat_cli_scripts.projects $2 -L --brief --csv "$3" > "$4" 2> /tmp/error_log.txt
}

# Set base folder and boilerplate arguments
BASE_FOLDER=$(dirname "$0")

# Corrected Boiler Plate with HTTPS URL and Hardcoded Password
BOILER_PLATE="-a kadic -x https://cnda-dev-archive1.nrg.wustl.edu -e False"

# Define input and output files
INPUT_FILE="/tmp/projects.txt"
OUTPUT_FILE="/tmp/projects_list.txt"

# Run the brief list function
list_projects_brief "$BASE_FOLDER" "$BOILER_PLATE" "$INPUT_FILE" "$OUTPUT_FILE"

# Confirm the output
echo "Brief list output saved to $OUTPUT_FILE"
ls -l "$OUTPUT_FILE"
cat /tmp/error_log.txt
