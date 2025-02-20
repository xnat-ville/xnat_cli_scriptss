#!/bin/python3
"""
projects.py
---
--------------------------------------------------------------------------------

This script interacts with a target XNAT instance to list and manage projects and users. 

Example usage:
    List all projects:
        python3 -m xnat_cli_scripts.projects -L

__version__ = (1, 0, 0)

"""

import argparse

import requests
import xnat
import xnat.core
import xnat.mixin

def format_project_header_rows() -> str:
    return "ID\tName\tInsert Date\tSubject Count\tExperiment Count\PI"
def format_project_data(project_json, project_object, args: argparse.Namespace) -> str:
    formatted_string=""
    if (args.brief_format is True):
        formatted_string = project_object.id
    elif (args.verbose is False):
        formatted_string = f"{project_object.id}\t{project_object.name}\t{len(project_object.subjects)}"
    else:
        pi_string = f"{project_json['pi_lastname']}, {project_json['pi_firstname']}"
        if (pi_string) == ", ":
            pi_string = "NONE"
        experiment_count = "Unknown"
        try:
            experiment_count = len(project_object.experiments)
        except KeyError:
            experiment_count = "Unknown"
        except requests.exceptions.ReadTimeout:
            experiment_count = "Unknown"

        formatted_string = f"{project_object.id}\t{project_object.name}\t{len(project_object.subjects)}\t{experiment_count}\t{pi_string}"

    return formatted_string

def format_project_id_name(p) -> str:
    return f"{p.id}, {p.name}"


def execute_list_projects(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    all_projects = session.get_json(f"/data/projects")
    result_set = all_projects['ResultSet']
    result     = result_set['Result']

    for project_json in result:
        project_object = session.projects[project_json['ID']]
        project_id = project_json['ID']
        project_name = project_json['name']
        print(format_project_data(project_json, project_object, args))

def execute_list_project_users(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    all_projects = session.get_json(f"/data/projects")

    result_set = all_projects['ResultSet']
    result     = result_set['Result']

    for project_json in result:
        project_object = session.projects[project_json['ID']]
        project_id = project_json['ID']
        users = connection.get_json(f"/data/projects/{project_id}/users")
        user_result_set = users['ResultSet']
        user_results    = user_result_set['Result']
        for user in user_results:
            print(f"{project_id}\t{user['login']}")

def execute_list_project_groups(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    all_projects = session.get_json(f"/data/projects")

    result_set = all_projects['ResultSet']
    result     = result_set['Result']

    for project_json in result:
        project_object = session.projects[project_json['ID']]
        project_id = project_json['ID']
        users = connection.get_json(f"/data/projects/{project_id}/users")
        user_result_set = users['ResultSet']
        user_results    = user_result_set['Result']
        for user in user_results:
            print(f"{project_id}\t{user['login']}\t{user['GROUP_ID']}")

def execute_list_master(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    if (args.users):
        execute_list_project_users(connection, args)
    elif (args.groups):
        execute_list_project_groups(connection, args)
    else:
        execute_list_projects(connection, args)



#def execute_project_list(session: xnat.session.XNATSession, args: argparse.Namespace) -> None:
#
#    print(format_project_header_rows())
#    all_projects = session.get_json(f"/data/projects")
#
#    result_set = all_projects['ResultSet']
#    result     = result_set['Result']
#
#    for project_json in result:
#        project_object = session.projects[project_json['ID']]
#        project_id = project_json['ID']
#        project_name = project_json['name']
#        project_pi = f"{project_json['pi_lastname']}, {project_json['pi_firstname']}"
#        z = session.get_json(f"/data/projects/{project_id}")
#        print(format_project_data(project_json, project_object))


def format_subject_header_rows() -> str:
    return "Project ID, Project Label, ID, Label, Insert Date, Experiment Count"
def format_subject_data(p) -> str:
    return f"{p.id}, {p.label}, {p.insert_date}, {len(p.experiments)} "

def execute_subject_list(session: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    if (args.subjects):
        print("\nSubject List")
        print(format_subject_header_rows())
        for proj in session.projects:
            project_header = format_project_id_name(session.projects[proj])
            for subject in session.projects[proj].subjects.values():
                print(f"{project_header}, {format_subject_data(subject)}")
                x = ""
                y = ""



def format_session_header_rows() -> str:
    return "Project ID, Project Label, ID, Label, Insert Date, Modality, Scan Count"
def format_session_data(p) -> str:
    return f"{p.id}, {p.label}, {p.insert_date}, {p.modality}, {len(p.scans)} "

def execute_session_list(session: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    if (args.sessions):
        print ("\nSession List")
        print(format_session_header_rows())
        for proj in session.projects:
            po = session.projects[proj]
            project_header = format_project_id_name(session.projects[proj])
            for experiment in po.experiments.values():
                print(f"{project_header} {format_session_data(experiment)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List projects from an XNAT system")
    parser.add_argument('-x', '--xnat',            dest='url',             help="URL to XNAT, default is https://cnda.wustl.edu")
    parser.add_argument('-a', '--auth',            dest='auth',            help="User authentication/login for access to XNAT", required=True)
    parser.add_argument('-e', '--extension_types', dest='extension_types', help="True or False for extension_types in xnat.connect")

    ## These are operations
    parser.add_argument('-L', '--list',            dest='list',            help="Action is to LIST",                  action='store_true')

    # These are objects of the operations; they regulate the action
    parser.add_argument('-u', '--users',           dest='users',           help='Verb object: Users',                 action='store_true')
    parser.add_argument('-g', '--groups',          dest='groups',          help='Verb object: Groups',                action='store_true')
    parser.add_argument(      '--subjects',        dest='subjects',        help="Include list of subjects in output", action='store_true')
    parser.add_argument(      '--sessions',        dest='sessions',        help="Include list of sessions in output", action='store_true')

    ## Further modifiers
    parser.add_argument('-b', '--brief',           dest='brief_format',    help="List in brief format",               action='store_true')
    parser.add_argument('-s', '--sleep',           dest='sleep',           help="Time to sleep after each REST call")
    parser.add_argument('-v', '--verbose',         dest='verbose',         help="Verbose mode",                       action='store_true')

    args = parser.parse_args()

    args.url = "https://cnda.wustl.edu" if args.url is None else args.url

#    print(args.extension_types)

#    password = None
    password = "admin"
    args.extension_types = "True" if args.extension_types is None else args.extension_types

    session = xnat.connect(args.url, user=args.auth, password=password, extension_types=bool(args.extension_types == "True"))


    if args.list:
        execute_list_master(session, args)


#    execute_project_list(session, args)
#    execute_subject_list(session, args)
#    execute_session_list(session, args)

    session.disconnect()

