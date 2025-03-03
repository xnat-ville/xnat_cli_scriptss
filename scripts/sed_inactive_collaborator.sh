#!/bin/sh

cat test_data/inactive_project_groups.txt	\
    | sed -e 's/owner$/collaborator/' -e 's/member$/collaborator/'	\
    > test_data/inactive_project_collaborators.txt

