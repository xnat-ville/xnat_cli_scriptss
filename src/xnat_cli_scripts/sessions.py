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

import xnat
import xnat.core
import xnat.mixin

def format_project_header_rows() -> str:
    return "ID, Name, Insert Date, Subject Count, Experiment Count"
def format_project_data(p) -> str:
    formatted_string = f"{p.id}, {p.name}, {p.insert_date}, {len(p.subjects)}, {len(p.experiments)}"
    return formatted_string

def format_project_id_name(p) -> str:
    return f"{p.id}, {p.name}"

def execute_project_list(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    print(format_project_header_rows())
    for proj in connection.projects:
        y = connection.projects[proj]
        print(format_project_data(y))

def format_subject_header_rows() -> str:
    return "Project ID, Project Label, ID, Label, Insert Date, Experiment Count"
def format_subject_data(p) -> str:
    return f"{p.id}, {p.label}, {p.insert_date}, {len(p.experiments)} "

def execute_subject_list(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    if (args.subjects):
        print("\nSubject List")
        print(format_subject_header_rows())
        for proj in connection.projects:
            project_header = format_project_id_name(connection.projects[proj])
            for subject in connection.projects[proj].subjects.values():
                print(f"{project_header}, {format_subject_data(subject)}")
                x = ""
                y = ""



def format_session_header_rows(brief_format_flag) -> str:
    if brief_format_flag is not None and brief_format_flag is True:
        return "Project ID\tSession ID\tSession Label"
    else:
        return "Project ID\tSession ID\tSession Label\tInsert Date\tModality\tScan Count"


def format_session_data(project_id, p, brief_format_flag) -> str:
    if brief_format_flag is not None and brief_format_flag is True:
        return f"{project_id}\t{p.id}\t{p.label}\t "
    else:
        return f"{project_id}\t{p.id}\t{p.label}\t{p.insert_date}\t{p.modality}\t{len(p.scans)} "

def execute_session_list(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    if (args.csv_file is None):
        print ("\nSession List")
        print(format_session_header_rows(args.brief_format))
        for proj in connection.projects:
            if (args.project_id is None or args.project_id == proj):
                po = connection.projects[proj]
                for experiment_obj in po.experiments.values():
                    print(format_session_data(proj, experiment_obj, args.brief_format))
    else:
        print("\nSelected Sessions")
        print(format_session_header_rows(args.brief_format))
        with open(args.csv_file, newline='') as csvfile:
            rdr = csv.reader(csvfile, delimiter='\t')
            for row in rdr:
                experiment_obj = connection.create_object(f"/data/projects/{row[0]}/experiments/{row[1]}")
                print(format_session_data(row[0], experiment_obj, args.brief_format))
#                print(f"{row[0]}\t{row[1]}\t{experiment_obj}\t{experiment_obj.id}")

def execute_session_delete(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    print("\nDelete Sessions")
    with open(args.csv_file, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter='\t')
        for row in rdr:
            experiment_obj = connection.create_object(f"/data/projects/{row[0]}/experiments/{row[1]}")
            print(f"{row[0]}\t{row[1]}\t{experiment_obj}")
            experiment_obj.delete(remove_files=True)

def execute_session_rename(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:

    print("\nRename Sessions")
    with open(args.csv_file, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter='\t')
        for row in rdr:
            experiment_obj = connection.create_object(f"/data/projects/{row[0]}/experiments/{row[1]}")
            subject_id = experiment_obj.subject_id
            experiment_id = experiment_obj.id
            query_arguments = {"label": row[2]}
            print(f"{row[0]}\t{row[1]}\t{row[2]}\t{experiment_obj} {query_arguments}")
            url_path=f"/REST/projects/{row[0]}/subjects/{subject_id}/experiments/{experiment_id}"
            print(f"{url_path} {query_arguments}")
            connection.put(url_path, query=query_arguments)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List projects from an XNAT system")
    parser.add_argument('-x', '--xnat',            dest='url',             help="URL to XNAT, default is https://cnda.wustl.edu")
    parser.add_argument('-u', '--user',            dest='user',            help="User login for access to XNAT", required=True)
    parser.add_argument('-e', '--extension_types', dest='extension_types', help="True or False for extension_types in xnat.connect")
    parser.add_argument('-c', '--csv_file',        dest='csv_file',        help="CSV file with list of sessions for operations")
    parser.add_argument('-l', '--list',            dest='list_sessions',   help="Action is to LIST sessions",    action='store_true')
    parser.add_argument('-b', '--brief',           dest='brief_format',    help="List in brief format",          action='store_true')
    parser.add_argument('-p', '--project',         dest='project_id',      help="Optional Project ID used in list process")
    parser.add_argument('-d', '--delete',          dest='delete_sessions', help="Action is to DELETE sessions",  action='store_true')
    parser.add_argument('-r', '--rename',          dest='rename_sessions', help="Action is to RENAME sessions",  action='store_true')

    args = parser.parse_args()

    args.url = "https://cnda.wustl.edu" if args.url is None else args.url
    args.extension_types = False if args.extension_types is None else args.extension_types

    password = None
#    password="admin"
    print(f"args.extension_types: {args.extension_types}")
    args.extension_types = "True" if args.extension_types is None else args.extension_types
    connection = xnat.connect(args.url, user=args.user, password=password, extension_types=False)

    if args.list_sessions:
        execute_session_list(connection, args)
    elif args.delete_sessions:
        execute_session_delete(connection, args)
    elif args.rename_sessions:
        execute_session_rename(connection, args)
    else:
        print("Neighbor list nor delete specified on commandline")

    connection.disconnect()

