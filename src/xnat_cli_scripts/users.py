#!/bin/python3
"""
sessions.py
---
--------------------------------------------------------------------------------
This application interacts with a target **XNAT**, and

Example usage of the CLI:
```bash
$ python3  [SCOPE]
```
"""

__version__ = (1, 0, 0)

import argparse
import csv
from time import sleep

import xnat
import xnat.core
import xnat.mixin

def execute_project_list(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    #print(format_project_header_rows())
    user_groups = connection.get_json(f"/xapi/users/smm/groups")

    for x_group in user_groups:
        connection.put(f"/xapi/users/test_user/groups/{x_group}")
        xyz = ""
        abc = ""

def execute_list_user_projects(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    target_user = args.target_user
    user_groups = connection.get_json(f"/xapi/users/{target_user}/groups")
    index = 1
    group_length = len(user_groups)
    float_sleep = 0.0
    if (args.sleep is not None):
        float_sleep = float(args.sleep)

    tab = "\t"
    for x_group in user_groups:
        role_index = x_group.rindex("_")
        project_only = x_group[:role_index]
        if args.verbose:
            print(f"{index}{tab}{group_length}{tab}{target_user}{tab}{project_only}")
            index += 1
        else:
            print(f"{target_user}{tab}{project_only}")

        sleep(float_sleep)

def execute_list_user_groups(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    target_user = args.target_user
    user_groups = connection.get_json(f"/xapi/users/{target_user}/groups")
    index = 1
    group_length = len(user_groups)
    float_sleep = 0.0
    if (args.sleep is not None):
        float_sleep = float(args.sleep)

    tab = "\t"
    for x_group in user_groups:
        if args.verbose:
            print(f"{index}{tab}{group_length}{tab}{target_user}{tab}{x_group}")
            index += 1
        else:
            print(f"{target_user}{tab}{x_group}")

        sleep(float_sleep)

def execute_list_user_roles(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    target_user = args.target_user
    user_roles = connection.get_json(f"/xapi/users/{target_user}/roles")
    index = 1
    role_length = len(user_roles)
    float_sleep = 0.0
    if (args.sleep is not None):
        float_sleep = float(args.sleep)

    tab = "\t"
    for x_role in user_roles:
        if args.verbose:
            print(f"{index}{tab}{role_length}{tab}{target_user}{tab}{x_role}")
            index += 1
        else:
            print(f"{target_user}{tab}{x_role}")

        sleep(float_sleep)

def execute_list_master(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    if (args.projects):
        execute_list_user_projects(connection, args)
    elif (args.roles):
        execute_list_user_roles(connection, args)
    elif (args.groups):
        execute_list_user_groups(connection, args)
    else:
        print("Request to list requires --projects or --roles")

def execute_user_group_clone(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    source_user = args.clone_groups
    target_user = args.target_user
    user_groups = connection.get_json(f"/xapi/users/{source_user}/groups")
    index = 1
    group_length = len(user_groups)
    float_sleep = 0.0
    if (args.sleep is not None):
        float_sleep = float(args.sleep)


    for x_group in user_groups:
        if args.verbose:
            print(f"{index} {group_length} {source_user} -> {target_user} : {x_group}")
            index += 1

        connection.put(f"/xapi/users/{target_user}/groups/{x_group}")
        sleep(float_sleep)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List projects from an XNAT system")

    ## XNAT user/login information
    parser.add_argument('-x', '--xnat',            dest='url',             help="URL to XNAT, default is https://cnda.wustl.edu")
    parser.add_argument('-u', '--user',            dest='user',            help="User login for access to XNAT", required=True)
    parser.add_argument('-e', '--extension_types', dest='extension_types', help="True or False for extension_types in xnat.connect")

    ## These are operations
    parser.add_argument('-L', '--list',            dest='list',            help="Action is to LIST",             action='store_true')
    parser.add_argument('-C', '--clone_groups',    dest='clone_groups',    help='Clone the user group from this user')
    parser.add_argument('-R', '--remove',          dest='remove',          help='Remove role(s) this user')

    # These are objects of the operations; they regulate the action
    parser.add_argument('-p', '--projects',        dest='projects',        help='Verb object: Projects',         action='store_true')
    parser.add_argument('-g', '--groups',          dest='groups',          help='Verb object: Groups',           action='store_true')
    parser.add_argument('-r', '--roles',           dest='roles',           help='Verb object: Roles',            action='store_true')
    parser.add_argument('-c', '--csv_file',        dest='csv_file',        help="CSV file with list of objects (projects, roles, ...) for operations")
    parser.add_argument('-t', '--target_user',     dest='target_user',     help='Target user: Operations performed on the target')

    ## Furhter modifiers
    parser.add_argument('-b', '--brief',           dest='brief_format',    help="List in brief format",          action='store_true')
    parser.add_argument('-s', '--sleep',           dest='sleep',           help="Time to sleep after each REST call")
    parser.add_argument('-v', '--verbose',         dest='verbose',         help="Verbose mode", action='store_true')
    parser.add_argument('-z', '--zebra',           dest='zebra',           help="Zebra mode for testing/debugging", action='store_true')

#    parser.add_argument('-p', '--project',         dest='project_id',      help="Optional Project ID used in list process")
#    parser.add_argument('-d', '--delete',          dest='delete_sessions', help="Action is to DELETE sessions",  action='store_true')
#    parser.add_argument('-r', '--rename',          dest='rename_sessions', help="Action is to RENAME sessions",  action='store_true')

    args = parser.parse_args()

    args.url = "https://cnda.wustl.edu" if args.url is None else args.url
    args.extension_types = False if args.extension_types is None else args.extension_types

    password = None
    password="admin"
    print(f"args.extension_types: {args.extension_types}")
    args.extension_types = "True" if args.extension_types is None else args.extension_types
    connection = xnat.connect(args.url, user=args.user, password=password, extension_types=False)

    if args.list:
        execute_list_master(connection, args)
    elif args.clone_groups:
        execute_user_group_clone(connection, args)
#    elif args.rename_sessions:
#        execute_session_rename(connection, args)
    else:
        print("Command not entered that we recognize")

    connection.disconnect()

