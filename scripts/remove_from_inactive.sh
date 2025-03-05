#!/bin/bash

# Arguments:
#              Base Folder
#              Boiler Plate
#              Output file

remove_projects_groups() {
    export PYTHONPATH="$1/../src"

    echo python3 -m xnat_cli_scripts.projects $2 --remove --groups
         python3 -m xnat_cli_scripts.projects $2 --remove --groups > "$3"
}

# Main starts here
# Arguments:
#               authentication string (user or user:password)

if [ $# -ne 1 ]; then
    echo "Arguments: auth_string"
    exit 1
fi

auth_string="$1"

BASE_FOLDER=`dirname $0`
source "$BASE_FOLDER/common.sh"
url=$(get_xnat_url)

BOILER_PLATE=" -a $auth_string -x $url -e False "

remove_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/inactive_project_groups.txt" test_data/inactive_project_groups_removal.txt