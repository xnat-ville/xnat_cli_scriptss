#!/bin/bash

# Arguments:
#              Base Folder
#              Boiler Plate
#              Output file
list_projects_brief() {
  export PYTHONPATH="$1/../src"

  echo python3 -m xnat_cli_scripts.projects $2 -L --brief
       python3 -m xnat_cli_scripts.projects $2 -L --brief > "$3"
}

# Main starts here
# Arguments:
#            authentication string (user or user:password)

if [ $# -ne 1 ]; then
  echo "Arguments: auth_string"
  exit 1
fi

auth_string="$1"

BASE_FOLDER=`dirname $0`
source "$BASE_FOLDER/common.sh"
url=$(get_xnat_url)

BOILER_PLATE=" -a $auth_string -x $url -e False "

list_projects_brief "$BASE_FOLDER" "$BOILER_PLATE" /tmp/projects_brief.txt
sort /tmp/projects_brief.txt | uniq > /tmp/all_projects_sorted.txt
sort test_data/inactive_projects.txt | uniq > /tmp/inactive_sorted.txt

diff /tmp/all_projects_sorted.txt /tmp/inactive_sorted.txt > /tmp/delta_projects.txt
grep "^< " /tmp/delta_projects.txt | sed -e 's/^< //' > test_data/active_projects.txt

wc -l test_data/inactive_projects.txt test_data/active_projects.txt