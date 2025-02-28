#!/bin/sh

# Arguments:
#              Base Folder
#              Boiler Plate
#              User ID (NA in this case)
#              Output file
list_projects_brief() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.projects $2 -L --brief
      python3 -m xnat_cli_scripts.projects $2 -L --brief > "$4"
}


 BASE_FOLDER=`dirname $0`
 BOILER_PLATE=" -a smoore -x https://cnda-dev-archive1.nrg.wustl.edu -e False "

 list_projects_brief "$BASE_FOLDER" "$BOILER_PLATE" NA-user /tmp/projects_brief.txt
 sort /tmp/projects_brief.txt | uniq > /tmp/all_projects_sorted.txt
 sort test_data/inactive_projects.txt | uniq > /tmp/inactive_sorted.txt

 diff /tmp/all_projects_sorted.txt /tmp/inactive_sorted.txt > /tmp/delta_projects.txt
 cat /tmp/delta_projects.txt | grep "^< " | sed -e 's/^< //' > test_data/active_projects.txt

 wc -l test_data/inactive_projects.txt test_data/active_projects.txt

