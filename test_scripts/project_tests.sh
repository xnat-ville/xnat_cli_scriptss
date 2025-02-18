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

list_projects_normal() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.projects $2 -L
      python3 -m xnat_cli_scripts.projects $2 -L > "$4"
}

list_projects_verbose() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.projects $2 -L --verbose
      python3 -m xnat_cli_scripts.projects $2 -L --verbose > "$4"
}

list_projects_users() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.projects $2 -L --users
      python3 -m xnat_cli_scripts.projects $2 -L --users > "$4"
}

list_projects_groups() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.projects $2 -L --groups
      python3 -m xnat_cli_scripts.projects $2 -L --groups > "$4"
}

# Arguments:
#              Base Folder
#              Boiler Plate
#              User ID
#              Output file
list_groups() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.users $2 -L --groups -t $3
      python3 -m xnat_cli_scripts.users $2 -L --groups -t $3 > "$4"
}

# Arguments:
#              Base Folder
#              Boiler Plate
#              CSV input file
#              Output file
remove_groups() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.users $2 -R --groups --csv "$3"
      python3 -m xnat_cli_scripts.users $2 -R --groups --csv "$3" > "$4"
}


 BASE_FOLDER=`dirname $0`
 BOILER_PLATE=" -a admin -x http://localhost:8080 -e False "

 list_projects_brief "$BASE_FOLDER" "$BOILER_PLATE" NA-user /tmp/projects_brief.txt
 ls -l /tmp/projects_brief.txt

 list_projects_normal "$BASE_FOLDER" "$BOILER_PLATE" NA-user /tmp/projects_normal.txt
 ls -l /tmp/projects_normal.txt

 list_projects_verbose "$BASE_FOLDER" "$BOILER_PLATE" NA-user /tmp/projects_verbose.txt
 ls -l /tmp/projects_verbose.txt

 list_projects_users "$BASE_FOLDER" "$BOILER_PLATE" NA-user /tmp/projects_users.txt
 ls -l /tmp/projects_users.txt

 list_projects_groups "$BASE_FOLDER" "$BOILER_PLATE" NA-user /tmp/projects_groups.txt
 ls -l /tmp/projects_groups.txt

