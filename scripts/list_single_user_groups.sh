#!/bin/bash


# Arguments:
#              Base Folder
#              Boiler Plate
#              User ID
#              Output file

list_groups() {
 export PYTHONPATH="$1/../src"
 echo PYTHONPATH $PYTHONPATH

 echo python3 -m xnat_cli_scripts.users $2 -L --groups -t $3
      python3 -m xnat_cli_scripts.users $2 -L --groups -t $3 
}

# Main starts here
# Arguments:
#            authentication string (user or user:password)
#            target user

 if [ $# -ne 2 ] ; then
  echo "Arguments: auth_string target_user"
  exit 1
 fi

 auth_string="$1"
 target_user="$2"

 BASE_FOLDER=`dirname $0`
 source $BASE_FOLDER/common.sh
 url=$( get_xnat_url )

 BOILER_PLATE=" -a $auth_string -x $url -e False "

 list_groups "$BASE_FOLDER" "$BOILER_PLATE" "$target_user"
 
