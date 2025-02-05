#!/bin/sh

# Arguments:
#              Base Folder
#              Boiler Plate
#              User ID
#              Output file
list_projects() {
 export PYTHONPATH="$1/../src"

 echo python3 -m xnat_cli_scripts.users $2 -L --projects -t $3
      python3 -m xnat_cli_scripts.users $2 -L --projects -t $3 > "$4"
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
 BOILER_PLATE=" -u admin -x http://localhost:8080 -e False "

 list_projects "$BASE_FOLDER" "$BOILER_PLATE" test_user /tmp/user_projects.txt
 ls -l /tmp/user_projects.txt

 list_groups "$BASE_FOLDER" "$BOILER_PLATE" test_user /tmp/user_groups.txt
 ls -l /tmp/user_groups.txt

 remove_groups "$BASE_FOLDER" "$BOILER_PLATE" /tmp/user_groups.txt /tmp/remove_status.txt
 ls -l /tmp/remove_status.txt

# remove_groups "$BASE_FOLDER" "$BOILER_PLATE" test_data/user_groups.txt /tmp/remove_user_groups.txt
# ls -l /tmp/remove_user_groups.txt
 
