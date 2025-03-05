#!/bin/python3


import argparse
from typing import Union

# Common functions for CLI executables

def extract_auth_user(args: argparse.Namespace) -> str:
    if (args.user is None):
        return "NoUser"

    return args.user.split(":")[0]

def extract_auth_password(args: argparse.Namespace) -> Union[str,None]:
    if (args.user is None):
        return None

    auth_tokens = args.user.split(":")
    auth_password=None

    if len(auth_tokens) > 1:
        auth_password = auth_tokens[1]
    elif args.password is not None:
        auth_password = args.password

    return auth_password

def extract_extension_types(args: argparse.Namespace) -> bool:
    if (args.extension_types is not None and args.extension_types == "True"):
        return True

    return False