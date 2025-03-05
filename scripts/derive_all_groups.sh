#!/bin/bash

# Arguments:
#              Base Folder
#              Boiler Plate
#              Output file

list_projects_groups() {
  export PYTHONPATH="$1/../src"

  echo python3 -m xnat_cli_scripts.projects $2 -L --groups
       python3 -m xnat_cli_scripts.projects $2 -L --groups > "$3"
}

# Main starts here
# Arguments:
#            authentication string (user or user:password)

if [ $# -ne 1 ]; then
  echo "Arguments: auth_string"
  exit 1
fi

auth_string="$1"

BASE_FOLDER=$(dirname "$0")
source "$BASE_FOLDER/common.sh"
url=$(get_xnat_url)

BOILER_PLATE=" -a $auth_string -x $url -e False "

list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/active_projects.txt" test_data/active_project_groups.txt
list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/inactive_projects.txt" test_data/inactive_project_groups.txt