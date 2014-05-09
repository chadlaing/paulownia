#!/usr/bin/env python

import argparse
import os

"""Gathers a single fasta sequence from each alignment file to use as a \
    query in the BLAST searches"""

parser = argparse.ArgumentParser()
parser.add_argument("aln_dir", help="The directory where the \
    single gene alignment files are stored")
parser.add_argument("out_file", help="Output file for query fasta")

args = parser.parse_args()
