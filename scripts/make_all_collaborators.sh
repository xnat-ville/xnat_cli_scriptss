#!/bin/sh

update_projects_groups() {
    export PYTHONPATH="$1/../src"

    echo python3 -m xnat_cli_scripts.projects $2 --update --groups
    python3 -m xnat_cli_scripts.projects $2 --update --groups > "$4"
}

# Main starts here

cnda_user="smoore"
if [ $# -ne 0 ] ; then
    cnda_user="$1"
fi

BASE_FOLDER=`dirname $0`
BOILER_PLATE=" -a $cnda_user -x https://cnda-dev-archive1.nrg.wustl.edu -e False "

update_projects_groups "$BASE_FOLDER" "$BOILER_PLATE --csv test_data/inactive_project_collaborators.txt" NA-user test_data/inactive_project_groups_update.txt
