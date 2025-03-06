#!/bin/bash

pre_flight() {
 for f in	\
	test_data/active_projects.txt	\
	test_data/inactive_projects.txt ; do
  if [ ! -f $f ] ; then
   echo Required file is missing: $f
   echo Script will exit now
   exit 1
  fi
 done
}

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
#            system (see common.sh)

if [ $# -ne 2 ]; then
  echo "Arguments: auth_string system"
  exit 1
fi

auth_string="$1"
system="$2"

BASE_FOLDER=$(dirname "$0")
source "$BASE_FOLDER/common.sh"
set -e
url=$(get_xnat_url ${system})
set +e

BOILER_PLATE=" -a $auth_string -x $url -e False "

pre_flight
list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/active_projects.txt" test_data/active_project_groups.txt
list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/inactive_projects.txt" test_data/inactive_project_groups.txt
