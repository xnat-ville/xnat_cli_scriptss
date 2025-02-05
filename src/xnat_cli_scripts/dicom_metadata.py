#!/bin/python3
"""
dicom_metadata.py
---
--------------------------------------------------------------------------------
This application extracts metadata from a DICOM file and formats per a profile

Example usage of the CLI:
```bash
$ python3  [SCOPE]
```
"""

__version__ = (1, 0, 0)

import argparse
import pydicom
from pydicom import dcmread
import csv


def extract_metadata(args) -> None:
    if (args.filename is None):
        print("Missing --filename option in the extract function")
        return

    tags = [0x00100010,
            0x00100020,
            0x00080016,
            0x00080020,
            0x00080030,
            0x00081010,
            0x0020000D]

    with open(args.filename, 'rb') as infile:
        output_str = ""
        delimiter_str = ""
        ds = dcmread(infile)
        for t in tags:
            gggg = (t >> 16) & 0xffff
            eeee = (t)       & 0xffff
            value_string = "'None'"
            if t in ds:
                v = ds[gggg, eeee]
                value_string = repr(v.value)

            output_str = output_str + delimiter_str + value_string
            delimiter_str = "\t"

#        if 'OriginalAttributesSequence' in ds:
#            original_attributes_sequence = ds.get('OriginalAttributesSequence')

        print(f"{args.filename}\t{output_str}")



    x = ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List projects from an XNAT system")
    parser.add_argument('-e', '--extract',         dest='extract_flag',    help="Action is to extract metadata",    action='store_true')
    parser.add_argument('-p', '--profile',         dest='profile',         help="Optional profile name to format output")
    parser.add_argument('-f', '--filename',        dest='filename',        help="Name of DICOM file to examine",    required=True)

    args = parser.parse_args()

    if args.extract_flag:
        extract_metadata(args)
    else:
        print("No action specified among the command line options")

