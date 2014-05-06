#!/usr/env python

from subprocess import call
import argparse

"""Gathers all aligned fasta files for single genes to create a concatenated \
    alignment file"""

parser = argparse.ArgumentParser()
parser.add_argument("alignment_directory", help="The directory where the \
    single gene alignment files are stored")

args = parser.parse_args()
print args.alignment_directory


# in_fh = open()
