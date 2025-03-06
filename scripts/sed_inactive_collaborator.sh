#!/bin/sh


pre_flight() {
 for f in       \
        test_data/inactive_project_groups.txt ; do
  if [ ! -f $f ] ; then
   echo Required file is missing: $f
   echo Script will exit now
   exit 1
  fi
 done
}

pre_flight
cat test_data/inactive_project_groups.txt	\
    | sed -e 's/owner$/collaborator/' -e 's/member$/collaborator/'	\
    > test_data/inactive_project_collaborators.txt

