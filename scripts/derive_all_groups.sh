#!/bin/sh

list_projects_groups() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.projects $2 -L --groups
      python3 -m xnat_cli_scripts.projects $2 -L --groups > "$4"
}

# Main starts here

 cnda_user="smoore"
 if [ $# -ne 0 ] ; then
  cnda_user="$1"
 fi


 BASE_FOLDER=`dirname $0`
 BOILER_PLATE=" -a $cnda_user -x https://cnda-dev-archive1.nrg.wustl.edu -e False "

 list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/active_projects.txt"   NA-user test_data/active_project_groups.txt
 list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/inactive_projects.txt" NA-user test_data/inactive_project_groups.txt

