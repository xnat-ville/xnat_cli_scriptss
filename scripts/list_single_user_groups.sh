#!/bin/bash

# Arguments:
#              Base Folder
#              Boiler Plate
#              User ID
#              Output file

list_groups() {
 export PYTHONPATH="$1/../src"
#echo PYTHONPATH $PYTHONPATH

 echo python3 -m xnat_cli_scripts.users $2 -L --groups -t $3
      python3 -m xnat_cli_scripts.users $2 -L --groups -t $3 
}

# Main starts here
# Arguments:
#            authentication string (user or user:password)
#            target user
#            system (found in common.sh)

 if [ $# -ne 3 ] ; then
  echo "Arguments: auth_string target_user system"
  exit 1
 fi

 auth_string="$1"
 target_user="$2"
 system="$3"

 BASE_FOLDER=`dirname $0`
 source $BASE_FOLDER/common.sh
 set -e
 url=$( get_xnat_url ${system} )
 set +e

 BOILER_PLATE=" -a $auth_string -x $url -e False "

 list_groups "$BASE_FOLDER" "$BOILER_PLATE" "$target_user"
 
