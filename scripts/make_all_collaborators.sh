#!/bin/bash

# Function to update project groups
update_projects_groups() {
    export PYTHONPATH="$1/../src"

    # Run the Python script with the update groups option, passing the password
    python3 -m xnat_cli_scripts.projects $2 --update --groups --password "$password" > "$4"
}

# Main starts here

# Default username is 'smoore', but can be overridden by a command line argument
cnda_user="smoore"
if [ $# -ne 0 ] ; then
    cnda_user="$1"
fi

# Define the base folder and the arguments to pass to the Python script
BASE_FOLDER=$(dirname "$0")
BOILER_PLATE=" -a $cnda_user -x https://cnda-dev-archive1.nrg.wustl.edu -e False "

# Prompt the user to enter the password securely using stty
echo "Enter password for $cnda_user:"
stty -echo  # Disable echo to hide the password
read password
stty echo   # Re-enable echo after the password is entered
echo         # Print a newline

# Call the function to update groups using the CSV file provided
update_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/inactive_project_collaborators.txt" NA-user test_data/inactive_project_groups_update.txt
