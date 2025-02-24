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
from xnat.session import XNATSession
import csv

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
    
    if args.csv_file:
        # Read project IDs from CSV file
        project_ids = []
        with open(args.csv_file, mode='r') as file:
            csv_reader = csv.reader(file, delimiter='\t')
            for row in csv_reader:
                project_ids.append(row[0])  # Assuming the project ID is in the first column

        # List only the projects from the CSV
        for project_id in project_ids:
            project_object = session.projects.get(project_id)
            if project_object:
                print(format_project_data({}, project_object, args))
    else:
        # List all projects as usual
        all_projects = session.get_json(f"/data/projects")
        result_set = all_projects['ResultSet']
        result = result_set['Result']

        for project_json in result:
            project_object = session.projects[project_json['ID']]
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

    # If a CSV file is provided, read the project IDs to limit the results
    if args.csv_file:
        project_ids = []
        with open(args.csv_file, mode='r') as file:
            csv_reader = csv.reader(file, delimiter='\t')
            for row in csv_reader:
                if row:  # Skip empty rows
                    project_ids.append(row[0].strip())  # Assuming the project ID is in the first column

        # Filter the results to only include the projects in the CSV
        result = [project for project in result if project['ID'] in project_ids]

    for project_json in result:
        project_id = project_json['ID']
        users = connection.get_json(f"/data/projects/{project_id}/users")
        user_result_set = users['ResultSet']
        user_results    = user_result_set['Result']
        for user in user_results:
            print(f"{project_id}\t{user['login']}\t{user['GROUP_ID']}")


def execute_remove_groups(connection: XNATSession, args: argparse.Namespace) -> None:
    """
    Remove groups specified in the CSV file.
    CSV Format: {project}{tab}{user}{tab}{group}
    This version removes the specified groups and appends "REMOVED" or "ERROR" to each line.
    """
    
    if args.csv_file:
        # Read the CSV file for groups to remove
        groups_to_remove = []

        try:
            with open(args.csv_file, mode='r') as file:
                csv_reader = csv.reader(file, delimiter='\t')
                for row in csv_reader:
                    # Verify row length and content
                    if len(row) < 3:
                        continue
                    
                    project = row[0].strip()  # Project ID
                    user = row[1].strip()     # User
                    group = row[2].strip()    # Group to be removed
                    
                    groups_to_remove.append((project, user, group))

        except FileNotFoundError:
            print(f"[ERROR] CSV file not found: {args.csv_file}")
            return
        except Exception as e:
            print(f"[ERROR] Exception while reading CSV: {e}")
            return

        # Iterate over each group and remove it
        for project, user, group in groups_to_remove:
            # XNAT API Call for group removal
            endpoint = f"/data/projects/{project}/users/{group}/{user}"
            full_url = f"{args.url}{endpoint}"  # Using args.url to construct the full URL

            try:
                response = requests.delete(full_url, auth=(args.auth, 'admin'), verify=False)
                if response.status_code == 200:
                    # Append REMOVED to the line if successful
                    print(f"{project}\t{user}\t{group}\tREMOVED")
                else:
                    # Append ERROR to the line if failed
                    print(f"{project}\t{user}\t{group}\tERROR")
            except requests.exceptions.RequestException:
                # If a request exception occurs, also append ERROR
                print(f"{project}\t{user}\t{group}\tERROR")

def execute_change_groups(connection: XNATSession, args: argparse.Namespace) -> None:
    """
    Change groups specified in the CSV file.
    CSV Format: {project}{tab}{user}{tab}{new_group}
    Detects group changes and:
      - Removes user from old group
      - Adds user to new group
    Echoes back the original input line and appends:
      - "CHANGED" if successful
      - "NO CHANGE" if no change was needed
      - "ERROR" if failed
    """

    if args.csv_file:
        # Read the CSV file for group changes
        groups_to_change = []

        try:
            with open(args.csv_file, mode='r') as file:
                csv_reader = csv.reader(file, delimiter='\t')
                for row in csv_reader:
                    # Ensure the row contains project ID, user, and group
                    if len(row) < 3:
                        continue
                    
                    project = row[0].strip()  # Project ID
                    user = row[1].strip()     # User
                    new_group = row[2].strip()  # New Group
                    
                    # Get current group
                    url = f"{args.url}/data/projects/{project}/users"
                    response = requests.get(url, auth=(args.auth, 'admin'), verify=False)

                    if response.status_code == 200:
                        # Search for the current group of the user
                        user_groups = response.json()['ResultSet']['Result']
                        current_group = None
                        for ug in user_groups:
                            if ug['login'] == user:
                                current_group = ug['GROUP_ID']
                                break

                        if current_group is None:
                            # User not found in this project
                            print(f"{project}\t{user}\t{new_group}\tERROR: User not found in project")
                            continue
                    else:
                        print(f"{project}\t{user}\t{new_group}\tERROR: Failed to fetch current group")
                        continue

                    # Check if the group has changed
                    if current_group != new_group:
                        # Remove from old group first
                        remove_endpoint = f"/data/projects/{project}/users/{current_group}/{user}"
                        remove_url = f"{args.url}{remove_endpoint}"

                        try:
                            response = requests.delete(remove_url, auth=(args.auth, 'admin'), verify=False)

                            if response.status_code == 200:
                                # Then add to the new group using the correct endpoint
                                add_endpoint = f"/data/projects/{project}/users/{new_group}/{user}"
                                add_url = f"{args.url}{add_endpoint}"

                                response = requests.put(add_url, auth=(args.auth, 'admin'), verify=False)

                                if response.status_code == 200:
                                    # Echo back the original input line and append CHANGED to {new_group}
                                    print(f"{project}\t{user}\t{new_group}\tCHANGED")
                                else:
                                    # If adding failed, print ERROR with details
                                    print(f"{project}\t{user}\t{new_group}\tERROR: Failed to add to new group - {response.status_code}")
                            else:
                                # If removing failed, print ERROR with details
                                print(f"{project}\t{user}\t{new_group}\tERROR: Failed to remove from old group - {response.status_code}")

                        except requests.exceptions.RequestException as e:
                            # If a request exception occurs, also append ERROR
                            print(f"{project}\t{user}\t{new_group}\tERROR: Request exception - {e}")
                    else:
                        # If no change was needed, print the current group with NO CHANGE
                        print(f"{project}\t{user}\t{new_group}\tNO CHANGE")

        except FileNotFoundError:
            print(f"[ERROR] CSV file not found: {args.csv_file}")
        except Exception as e:
            print(f"[ERROR] Exception while reading CSV: {e}")



def execute_list_project_accessibilities(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    """
    Lists project accessibilities (private/public/protected)
    Output format: {project}{tab}{accessibility}
    """
    project_ids = []

    # If CSV file is specified, read project IDs from CSV
    if args.csv_file:
        with open(args.csv_file, mode='r') as file:
            csv_reader = csv.reader(file, delimiter='\t')
            for row in csv_reader:
                project_ids.append(row[0])  # Assuming project ID is in the first column

    # Get all projects
    all_projects = connection.get_json(f"/data/projects")
    result_set = all_projects['ResultSet']
    result = result_set['Result']

    for project_json in result:
        project_id = project_json['ID']

        # If CSV is used, check if the project is in the CSV list
        if args.csv_file and project_id not in project_ids:
            continue

        # Get accessibility using requests directly since the endpoint returns plain text
        url = f"{args.url}/data/projects/{project_id}/accessibility"
        response = requests.get(url, auth=(args.auth, 'admin'), verify=False)
        
        if response.status_code == 200:
            accessibility = response.text.strip()  # Plain text response
        else:
            accessibility = "Unknown"  # Fallback for error cases
        
        print(f"{project_id}\t{accessibility}")

def execute_update_accessibilities(connection: XNATSession, args: argparse.Namespace) -> None:
    """
    Update the accessibility of projects based on the CSV file.
    CSV Format: {project_id}{tab}{new_accessibility}
    The system checks the current accessibility in XNAT and updates it if necessary.
    Echoes back the original input line and appends "UPDATED" or "ERROR".
    """

    if args.csv_file:
        # Read the CSV file for project accessibility updates
        projects_to_update = []

        try:
            with open(args.csv_file, mode='r') as file:
                csv_reader = csv.reader(file, delimiter='\t')
                for row in csv_reader:
                    # Ensure the row contains both project ID and accessibility
                    if len(row) < 2:
                        continue
                    
                    project_id = row[0].strip()  # Project ID
                    new_accessibility = row[1].strip().lower()  # New accessibility (private, public, protected)
                    
                    # Only accept valid accessibility values
                    if new_accessibility not in ['private', 'public', 'protected']:
                        print(f"[ERROR] Invalid accessibility '{new_accessibility}' for project {project_id}. Skipping.")
                        continue
                    
                    projects_to_update.append((project_id, new_accessibility))

        except FileNotFoundError:
            print(f"[ERROR] CSV file not found: {args.csv_file}")
            return
        except Exception as e:
            print(f"[ERROR] Exception while reading CSV: {e}")
            return

        # Iterate over each project and update accessibility
        for project_id, new_accessibility in projects_to_update:
            # Get current accessibility for the project (plain text)
            url = f"{args.url}/data/projects/{project_id}/accessibility"
            response = requests.get(url, auth=(args.auth, 'admin'), verify=False)

            if response.status_code == 200:
                current_accessibility = response.text.strip().lower()
            else:
                print(f"[ERROR] Could not fetch current accessibility for project '{project_id}'. Skipping.")
                continue

            if current_accessibility != new_accessibility:
                # Accessibility does not match, so update it
                endpoint = f"/data/projects/{project_id}/accessibility/{new_accessibility}"
                full_url = f"{args.url}{endpoint}"

                try:
                    # Update the project accessibility via XNAT API
                    response = requests.put(full_url, auth=(args.auth, 'admin'), verify=False)

                    if response.status_code == 200:
                        # Echo back the original input line and append UPDATED to {new_accessibility} with a tab
                        print(f"{project_id}\t{new_accessibility}\tUPDATED")
                    else:
                        # If there's a failure, append ERROR with a tab
                        print(f"{project_id}\t{new_accessibility}\tERROR")
                
                except requests.exceptions.RequestException as e:
                    # If a request exception occurs, also append ERROR with a tab
                    print(f"{project_id}\t{new_accessibility}\tERROR")
            else:
                # If no update was needed, print the current accessibility with NO CHANGE with a tab
                print(f"{project_id}\t{new_accessibility}\tNO CHANGE")


def execute_list_master(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    # Check for UPDATE action first (Change Groups)
    if args.update and args.groups:
        # If CSV is provided, use it for changing groups
        if args.csv_file:
            execute_change_groups(connection, args)
        else:
            print("[WARNING] No CSV file provided. Please specify --csv for changing groups.")
        return  # Exit after changing groups

    # Check for UPDATE action (Update Accessibilities)
    if args.update and args.accessibilities:
        # If CSV is provided, use it for updating accessibilities
        if args.csv_file:
            execute_update_accessibilities(connection, args)
        else:
            print("[WARNING] No CSV file provided. Please specify --csv for updating accessibilities.")
        return  # Exit after updating accessibilities

    # Check for REMOVE action next
    if args.remove and args.groups:
        # If CSV is provided, use it to get groups for removal
        if args.csv_file:
            execute_remove_groups(connection, args)
        else:
            print("[WARNING] No CSV file provided. Please specify --csv for group removal.")
        return  # Exit after removing groups

    # Check for LIST actions last
    if args.users:
        execute_list_project_users(connection, args)
    elif args.groups:
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
    parser.add_argument('-x', '--xnat',            dest='url',                      help="URL to XNAT, default is https://cnda.wustl.edu")
    parser.add_argument('-a', '--auth',            dest='auth',                     help="User authentication/login for access to XNAT", required=True)
    parser.add_argument('-e', '--extension_types', dest='extension_types',          help="True or False for extension_types in xnat.connect")

    ## These are operations
    parser.add_argument('-L', '--list',            dest='list',                     help="Action is to LIST",                          action='store_true')
    parser.add_argument('-R', '--remove',          dest='remove',                   help='Remove groups from projects',                action='store_true')
    parser.add_argument(        '--update',        dest='update',                   help='Update project accessibilities',             action='store_true')

    # These are objects of the operations; 
    parser.add_argument('-u', '--users',           dest='users',                    help='Listing Verb object: Users',                 action='store_true')
    parser.add_argument('-g', '--groups',          dest='groups',                   help='Object: Groups (for both LIST and REMOVE)',  action='store_true')
    parser.add_argument(      '--accessibilities', dest='accessibilities',          help="Accessibilities for projects",                action='store_true')
    parser.add_argument(      '--subjects',        dest='subjects',                 help="Include list of subjects in output",         action='store_true')
    parser.add_argument(      '--sessions',        dest='sessions',                 help="Include list of sessions in output",         action='store_true')


    ## Further modifiers
    parser.add_argument('-b', '--brief',           dest='brief_format',             help="List in brief format",                       action='store_true')
    parser.add_argument('-s', '--sleep',           dest='sleep',                    help="Time to sleep after each REST call")
    parser.add_argument('-v', '--verbose',         dest='verbose',                  help="Verbose mode",                               action='store_true')
    parser.add_argument('--csv',                   dest='csv_file',                 help='Path to CSV file operations such as listing, removing, or changing groups')
    
    args = parser.parse_args()

    args.url = "http://localhost" if args.url is None else args.url

#    print(args.extension_types)

#    password = None
    password = "admin"
    args.extension_types = "True" if args.extension_types is None else args.extension_types

    session = xnat.connect(args.url, user=args.auth, password=password, extension_types=bool(args.extension_types == "True"))


if args.list or args.remove or args.update or args.change_groups:
    execute_list_master(session, args)


#    execute_project_list(session, args)
#    execute_subject_list(session, args)
#    execute_session_list(session, args)

    session.disconnect()

