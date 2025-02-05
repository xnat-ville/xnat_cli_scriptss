#!/bin/python3
"""
delete.py
---
--------------------------------------------------------------------------------
This applicatiob interacts with a target **XNAT**, and deletes one or more
objects (subject, session) from a list of labels or identifiers supplied
at the command line inpout.

Example usage of the CLI:
```bash
$ python3 -m xport_manifest -X <xnat_name> [search_opts] [SCOPE]
```
"""

__version__ = (1, 0, 0)

import argparse
#import contextlib
#import enum
#import io
#import math
#import os
#import pathlib
#import re
#import sys
#import tempfile
#import typing
#import urllib.parse

#import click
#import fabric
import xnat
import xnat.core
import xnat.mixin
#import yaml





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete objects from an XNAT system")
    parser.add_argument("list")
    parser.add_argument('-u', '--url',   dest='url',   help="URL to XNAT, default is https://cnda.wustl.edu")

    args = parser.parse_args()

    args.url = "https://cnda.wustl.edu" if args.url is None else args.url

    print(args.url, args.list)
