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
import time


# Time Helper Function

def apply_sleep(args: argparse.Namespace) -> None:
    """ Applies sleep if -s is specified """
    if args.sleep:
        try:
            sleep_time = float(args.sleep)
            if sleep_time > 0:
                time.sleep(sleep_time)
        except ValueError:
            print("[ERROR] Invalid sleep value. Please provide a valid number.")


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
                # Apply sleep after processing each project
                apply_sleep(args)
    else:
        # List all projects as usual
        all_projects = session.get_json(f"/data/projects")
        # Apply sleep after the REST call (moved up here)
        apply_sleep(args)

        result_set = all_projects['ResultSet']
        result = result_set['Result']

        for project_json in result:
            project_object = session.projects[project_json['ID']]
            print(format_project_data(project_json, project_object, args))
            # Apply sleep after processing each project
            apply_sleep(args)


def execute_list_project_users(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    # Check if CSV file is provided
    if args.csv_file:  # Correctly reference args.csv_file
        # Read the CSV file and get the list of project IDs
        project_ids_from_csv = []
        with open(args.csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:  # Ensure that the row is not empty
                    project_ids_from_csv.append(row[0].strip())  # Append project IDs from CSV
    else:
        project_ids_from_csv = None

    all_projects = session.get_json(f"/data/projects")
    # Apply sleep after the main REST call
    apply_sleep(args)

    result_set = all_projects['ResultSet']
    result = result_set['Result']

    for project_json in result:
        project_id = project_json['ID']

        # If CSV is provided, only process projects in the CSV file
        if project_ids_from_csv and project_id not in project_ids_from_csv:
            continue

        users = connection.get_json(f"/data/projects/{project_id}/users")
        # Apply sleep after fetching users for each project
        apply_sleep(args)

        user_result_set = users['ResultSet']
        user_results = user_result_set['Result']

        for user in user_results:
            print(f"{project_id}\t{user['login']}")
        
        # Apply sleep after processing each project's users
        apply_sleep(args)




def execute_list_project_groups(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    all_projects = session.get_json(f"/data/projects")
    # Apply sleep after the main REST call
    apply_sleep(args)

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
        # Apply sleep after fetching users for each project
        apply_sleep(args)

        user_result_set = users['ResultSet']
        user_results    = user_result_set['Result']

        for user in user_results:
            print(f"{project_id}\t{user['login']}\t{user['GROUP_ID']}")
        
        # Apply sleep after processing each project's groups
        apply_sleep(args)


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
                # Apply sleep after each REST call
                apply_sleep(args)

                if response.status_code == 200:
                    # Append REMOVED to the line if successful
                    print(f"{project}\t{user}\t{group}\tREMOVED")
                else:
                    # Append ERROR to the line if failed
                    print(f"{project}\t{user}\t{group}\tERROR")
            except requests.exceptions.RequestException:
                # If a request exception occurs, also append ERROR
                print(f"{project}\t{user}\t{group}\tERROR")
            
            # Apply sleep after processing each line in the CSV
            apply_sleep(args)


def execute_update_groups(connection: XNATSession, args: argparse.Namespace) -> None:
    """
    Update groups specified in the CSV file.
    CSV Format: {project}{tab}{user}{tab}{new_group}
    Adds user to the new group.
    Since XNAT automatically removes user from old group, no need to check or delete old group.
    Echoes back the original input line and appends:
      - "CHANGED" if successful
      - "ERROR" if failed
    """

    if args.csv_file:
        # Read the CSV file for group changes
        groups_to_update = []

        try:
            with open(args.csv_file, mode='r') as file:
                csv_reader = csv.reader(file, delimiter='\t')
                for row in csv_reader:
                    # Ensure the row contains project ID, user, and group
                    if len(row) < 3:
                        print(f"[ERROR] Invalid row format: {row}. Expected format: project_id\tuser\tnew_group")
                        continue
                    
                    project = row[0].strip()  # Project ID
                    user = row[1].strip()     # User
                    new_group = row[2].strip()  # New Group
                    
                    groups_to_update.append((project, user, new_group))

        except FileNotFoundError:
            print(f"[ERROR] CSV file not found: {args.csv_file}")
            return
        except Exception as e:
            print(f"[ERROR] Exception while reading CSV: {e}")
            return

        # Iterate over each group and update it
        for project, user, new_group in groups_to_update:
            # Add to the new group using the correct endpoint
            add_endpoint = f"/data/projects/{project}/users/{new_group}/{user}"
            add_url = f"{args.url}{add_endpoint}"

            try:
                response = requests.put(add_url, auth=(args.auth, 'admin'), verify=False)
                # Apply sleep after each REST call
                apply_sleep(args)

                if response.status_code == 200:
                    # Echo back the original input line and append CHANGED to {new_group}
                    print(f"{project}\t{user}\t{new_group}\tCHANGED")
                else:
                    # If adding failed, print ERROR with details
                    print(f"{project}\t{user}\t{new_group}\tERROR: Failed to add to new group - {response.status_code}")

            except requests.exceptions.RequestException as e:
                # If a request exception occurs, also append ERROR
                print(f"{project}\t{user}\t{new_group}\tERROR: Request exception - {e}")
            
            # Apply sleep after processing each line in the CSV
            apply_sleep(args)


def execute_list_project_accessibilities(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    """
    Lists project accessibilities (private/public/protected).
    Output format: {project}{tab}{accessibility}.
    """
    project_ids = []

    # If CSV file is specified, read project IDs from CSV
    if args.csv_file:
        with open(args.csv_file, mode='r') as file:
            csv_reader = csv.reader(file, delimiter='\t')
            project_ids_from_csv = [row[0].strip() for row in csv_reader if row]  # Handle empty rows
    else:
        project_ids_from_csv = None

    # Get all projects
    all_projects = connection.get_json(f"/data/projects")
    # Apply sleep after the main REST call
    apply_sleep(args)

    result_set = all_projects['ResultSet']
    result = result_set['Result']

    for project_json in result:
        project_id = project_json.get('ID', None)
        if not project_id:
            print(f"[ERROR] Missing 'ID' for project: {project_json}")
            continue

        # If CSV is used, check if the project is in the CSV list
        if args.csv_file and project_id not in project_ids_from_csv:
            continue

        # Get accessibility using requests directly (plain text response)
        url = f"{args.url}/data/projects/{project_id}/accessibility"
        response = requests.get(url, auth=(args.auth, 'admin'), verify=False)  # Keep verify=False to avoid SSL warnings
        
        # Apply sleep after each REST call for accessibility
        apply_sleep(args)

        if response.status_code == 200:
            accessibility = response.text.strip()  # Ensure plain text handling (no JSON parsing)
        else:
            print(f"[ERROR] Failed to retrieve accessibility for {project_id}: {response.status_code}")
            accessibility = "Unknown"

        # Print the project ID and its accessibility
        print(f"{project_id}\t{accessibility}")

        # Apply sleep after processing each project
        apply_sleep(args)



def execute_update_accessibilities(connection: XNATSession, args: argparse.Namespace) -> None:
    """
    Update the accessibility of projects based on the CSV file.
    CSV Format: {project_id}{tab}{new_accessibility}
    The system checks the current accessibility in XNAT and updates it if necessary.
    Echoes back the original input line and appends "UPDATED", "ERROR", or "NO CHANGE".
    """

    if args.csv_file:
        try:
            with open(args.csv_file, mode='r') as file:
                csv_reader = csv.reader(file, delimiter='\t')
                for row in csv_reader:
                    if len(row) < 2:
                        continue
                    
                    project_id, new_accessibility = row[0].strip(), row[1].strip().lower()

                    if new_accessibility not in ['private', 'public', 'protected']:
                        print(f"[ERROR] Invalid accessibility '{new_accessibility}' for project {project_id}. Skipping.")
                        continue

                    # Get current accessibility for the project (plain text)
                    url = f"{args.url}/data/projects/{project_id}/accessibility"
                    response = requests.get(url, auth=(args.auth, 'admin'), verify=False)
                    # Apply sleep after each GET call for current accessibility
                    apply_sleep(args)

                    if response.status_code == 200:
                        current_accessibility = response.text.strip().lower()
                    else:
                        print(f"[ERROR] Could not fetch current accessibility for project '{project_id}'. Skipping.")
                        continue

                    if current_accessibility != new_accessibility:
                        # Accessibility does not match, so update it
                        endpoint = f"/data/projects/{project_id}/accessibility/{new_accessibility}"
                        full_url = f"{args.url}{endpoint}"

                        response = requests.put(full_url, auth=(args.auth, 'admin'), verify=False)
                        # Apply sleep after each PUT call for updating accessibility
                        apply_sleep(args)

                        if response.status_code == 200:
                            print(f"{project_id}\t{new_accessibility}\tUPDATED")
                        else:
                            print(f"{project_id}\t{new_accessibility}\tERROR")
                    else:
                        # If no update was needed, print the current accessibility with NO CHANGE with a tab
                        print(f"{project_id}\t{new_accessibility}\tNO CHANGE")
                    
                    # Apply sleep after processing each line in the CSV
                    apply_sleep(args)

        except FileNotFoundError:
            print(f"[ERROR] CSV file not found: {args.csv_file}")
        except Exception as e:
            print(f"[ERROR] Exception while reading CSV: {e}")


def execute_list_master(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    # Check for LIST actions first
    if args.users:
        execute_list_project_users(connection, args)
    elif args.groups:
        execute_list_project_groups(connection, args)
    elif args.accessibilities:
        execute_list_project_accessibilities(connection, args)
    else:
        execute_list_projects(connection, args)


def execute_remove_master(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    # Check for REMOVE action
    if args.remove and args.groups:
        # If CSV is provided, use it to get groups for removal
        if args.csv_file:
            execute_remove_groups(connection, args)
        else:
            print("[WARNING] No CSV file provided. Please specify --csv for group removal.")
    else:
        print("[WARNING] Invalid REMOVE action. Use -R with -g and --csv.")


def execute_update_master(connection: xnat.session.XNATSession, args: argparse.Namespace) -> None:
    # Check for UPDATE action (Change Groups)
    if args.update and args.groups:
        # If CSV is provided, use it for changing groups
        if args.csv_file:
            execute_update_groups(connection, args)
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
    else:
        print("[WARNING] Invalid UPDATE action. Use --update with --accessibilities or -g and --csv.")


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
    parser.add_argument('-p', '--password', dest='password', help="Password for XNAT authentication", required=True)
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

#    password = "admin"
 
    # session = xnat.connect(args.url, user=args.auth, password=password, extension_types=False)
    session = xnat.connect(args.url, extension_types=False, user=args.auth, password=args.password)

if args.list:
    execute_list_master(session, args)
elif args.remove:
    execute_remove_master(session, args)
elif args.update:
    execute_update_master(session, args)
else:
    print("[ERROR] No valid action specified. Use -L, -R, or --update.")


#    execute_project_list(session, args)
#    execute_subject_list(session, args)
#    execute_session_list(session, args)

    session.disconnect()

